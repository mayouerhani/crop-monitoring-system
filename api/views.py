from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404

from monitoring.models import Plot, SensorReading, Alert
from .ai_agent_engine import CropMonitoringAgent, AnomalySeverity
from .serializers import PlotSerializer, AlertSerializer, SensorReadingSerializer


class AlertViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Alert.objects.filter(plot__user=user).order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        cutoff_time = datetime.now() - timedelta(hours=24)
        alerts = self.get_queryset().filter(timestamp__gte=cutoff_time)
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        alerts = self.get_queryset().filter(severity='critical')
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_plot(self, request):
        plot_id = request.query_params.get('plot_id')
        if plot_id:
            alerts = self.get_queryset().filter(plot_id=plot_id)
        else:
            alerts = self.get_queryset()
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        alerts = self.get_queryset()
        summary = {
            "total_alerts": alerts.count(),
            "critical": alerts.filter(severity='critical').count(),
            "high": alerts.filter(severity='high').count(),
            "medium": alerts.filter(severity='medium').count(),
            "low": alerts.filter(severity='low').count(),
            "by_type": {}
        }
        
        alert_types = ['temperature', 'humidity', 'soil_moisture', 'ph_level', 'light_intensity']
        for alert_type in alert_types:
            summary["by_type"][alert_type] = alerts.filter(alert_type=alert_type).count()
        
        return Response(summary)


class SensorReadingAnalysisViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def analyze_latest(self, request):
        """Analyze latest sensor readings for a plot"""
        plot_id = request.data.get('plot_id')
        
        if not plot_id:
            return Response(
                {"error": "plot_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            plot = Plot.objects.get(id=plot_id, user=request.user)
        except Plot.DoesNotExist:
            return Response(
                {"error": "Plot not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get latest sensor readings
        sensor_data = {}
        sensor_types = ['temperature', 'humidity', 'soil_moisture', 'ph_level', 'light_intensity']
        
        for sensor_type in sensor_types:
            try:
                latest = SensorReading.objects.filter(
                    plot=plot,
                    sensor_type=sensor_type
                ).latest('timestamp')
                sensor_data[sensor_type] = latest.value
            except SensorReading.DoesNotExist:
                continue
        
        if not sensor_data:
            return Response(
                {"error": "No sensor readings available"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Run AI Agent analysis
        agent = CropMonitoringAgent()
        alerts = agent.analyze_sensor_data(
            sensor_data=sensor_data,
            plot_id=str(plot_id),
            timestamp=datetime.now().isoformat()
        )
        
        # Save alerts to database
        saved_alerts = []
        for alert in alerts:
            db_alert = Alert.objects.create(
                plot=plot,
                alert_type=alert.alert_type.value,
                severity=alert.severity.value,
                message=alert.message,
                current_value=alert.current_value,
                threshold_value=alert.threshold_value,
                recommendations=alert.recommendations,
                timestamp=datetime.fromisoformat(alert.timestamp)
            )
            saved_alerts.append(db_alert)
        
        serializer = AlertSerializer(saved_alerts, many=True)
        return Response({
            "alerts_generated": len(saved_alerts),
            "alerts": serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def batch_analyze(self, request):
        """Analyze all plots"""
        plots = Plot.objects.filter(user=request.user)
        all_alerts = []
        
        agent = CropMonitoringAgent()
        
        for plot in plots:
            sensor_types = ['temperature', 'humidity', 'soil_moisture', 'ph_level', 'light_intensity']
            sensor_data = {}
            
            for sensor_type in sensor_types:
                try:
                    latest = SensorReading.objects.filter(
                        plot=plot,
                        sensor_type=sensor_type
                    ).latest('timestamp')
                    sensor_data[sensor_type] = latest.value
                except SensorReading.DoesNotExist:
                    continue
            
            if sensor_data:
                alerts = agent.analyze_sensor_data(
                    sensor_data=sensor_data,
                    plot_id=str(plot.id),
                    timestamp=datetime.now().isoformat()
                )
                
                for alert in alerts:
                    Alert.objects.create(
                        plot=plot,
                        alert_type=alert.alert_type.value,
                        severity=alert.severity.value,
                        message=alert.message,
                        current_value=alert.current_value,
                        threshold_value=alert.threshold_value,
                        recommendations=alert.recommendations,
                        timestamp=datetime.fromisoformat(alert.timestamp)
                    )
                    all_alerts.extend(alerts)
        
        return Response({
            "total_alerts_generated": len(all_alerts),
            "plots_analyzed": plots.count()
        })


class PlotViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PlotSerializer
    
    def get_queryset(self):
        return Plot.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def sensor_data_summary(self, request, pk=None):
        plot = self.get_object()
        sensor_types = ['temperature', 'humidity', 'soil_moisture', 'ph_level', 'light_intensity']
        summary = {}
        
        for sensor_type in sensor_types:
            try:
                latest = SensorReading.objects.filter(
                    plot=plot,
                    sensor_type=sensor_type
                ).latest('timestamp')
                
                summary[sensor_type] = {
                    "value": latest.value,
                    "unit": latest.unit,
                    "timestamp": latest.timestamp
                }
            except SensorReading.DoesNotExist:
                summary[sensor_type] = None
        
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def active_alerts(self, request, pk=None):
        plot = self.get_object()
        alerts = Alert.objects.filter(plot=plot, is_resolved=False).order_by('-timestamp')
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)