
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
from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status

from monitoring.models import SensorReading, AnomalyEvent, AgentRecommendation, FieldPlot
from .serializers import (
    SensorReadingSerializer,
    AnomalyEventSerializer,
    AgentRecommendationSerializer
)

# ============================================================================
# 1. VUE RACINE DE L'API
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Page d'accueil de l'API"""
    return Response({
        'project': 'AI-Enhanced Crop Monitoring System',
        'version': '1.0',
        'author': 'Chaouki Bayoudhi',
        'endpoints': {
            'sensor_readings': {
                'create': 'POST /api/sensor-readings/create/',
                'list': 'GET /api/sensor-readings/',
                'filter_examples': [
                    '/api/sensor-readings/?plot=1',
                    '/api/sensor-readings/?sensor_type=soil_moisture'
                ]
            },
            'anomalies': 'GET /api/anomalies/',
            'recommendations': 'GET /api/recommendations/',
            'sensors': 'POST /api/sensors/'
        },
        'note': 'Use the endpoints above to interact with the system'
    })


# ============================================================================
# 2. ENDPOINT BATCH - CORRECTION DES BUGS UNIQUEMENT
# ============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def sensor_add(request):
    """Endpoint batch pour ajouter plusieurs lectures"""
    print("\n" + "="*60)
    print("🔄 sensor_add() CALLED")
    
    try:
        data = request.data
        print(f"📦 Data received: {data}")
        
        plot_id = data.get('plot_id')
        readings = data.get('readings', [])
        
        print(f"📍 plot_id: {plot_id}")
        print(f"📊 readings count: {len(readings)}")
        
        if not plot_id or not readings:
            print("❌ ERROR: plot_id or readings missing")
            return Response(
                {'error': 'plot_id and readings are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Convert plot_id to int
        try:
            plot_id_int = int(plot_id)
        except:
            print(f"❌ Invalid plot_id: {plot_id}")
            return Response(
                {'error': 'plot_id must be a number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifie que le plot existe
        try:
            plot = FieldPlot.objects.get(id=plot_id_int)
            print(f"✅ Plot exists: {plot.name}")
        except FieldPlot.DoesNotExist:
            print(f"❌ Plot {plot_id_int} does not exist")
            return Response(
                {'error': f'Plot {plot_id_int} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Mappage des capteurs - correspond aux SENSOR_TYPES dans models.py
        sensor_map = {
            'moisture': ('moisture', 'percentage'),
            'soil_moisture': ('moisture', 'percentage'),
            'temperature': ('temperature', 'celsius'),
            'air_temperature': ('temperature', 'celsius'),
            'temp': ('temperature', 'celsius'),
            'humidity': ('humidity', 'percentage'),
            'hum': ('humidity', 'percentage'),
            'ph': ('ph', 'ph'),
            'nitrogen': ('nitrogen', 'ppm')
        }
        
        created_count = 0
        anomaly_detected = False
        
        for i, reading in enumerate(readings):
            print(f"\n📝 Processing reading {i}: {reading}")
            
            sensor = reading.get('sensor')
            value = reading.get('value')
            
            print(f"  sensor: '{sensor}'")
            print(f"  value: {value}")
            
            if sensor and value is not None:
                sensor_lower = str(sensor).lower().strip()
                print(f"  sensor_lower: '{sensor_lower}'")
                
                if sensor_lower in sensor_map:
                    print(f"  ✅ Sensor recognized")
                    
                    try:
                        value_float = float(value)
                        
                        # 🔧 BUG FIX: Déstructurer le tuple AVANT create()
                        sensor_type, unit = sensor_map[sensor_lower]
                        
                        # Crée la lecture avec TOUS les champs requis
                        sensor_reading = SensorReading.objects.create(
                            plot=plot,
                            sensor_type=sensor_type,
                            value=value_float,       # 🔧 CORRIGÉ: ce champ manquait!
                            unit=unit
                        )
                        created_count += 1
                        print(f"  ✅ SensorReading created: ID {sensor_reading.id}")
                        
                        # Détection d'anomalie simple
                        if sensor_lower in ['moisture', 'soil_moisture'] and value_float < 30:
                            anomaly_detected = True
                            print(f"  ⚠️ ANOMALY DETECTED: moisture={value_float}")
                            
                            # Crée l'anomalie
                            anomaly = AnomalyEvent.objects.create(
                                plot=plot,
                                anomaly_type='moisture_drop',
                                severity='high',
                                detected_value=value_float,
                                normal_range_min=30,
                                normal_range_max=80,
                                model_confidence=0.9
                            )
                            print(f"  ✅ AnomalyEvent created: ID {anomaly.id}")
                            
                            # Crée la recommandation
                            recommendation = AgentRecommendation.objects.create(
                                anomaly_event=anomaly,
                                recommended_action='irrigation',
                                action_details='Increase irrigation immediately',
                                explanation_text=f'Soil moisture ({value_float}%) is critically low (below 30%)',
                                confidence='high'
                            )
                            print(f"  ✅ AgentRecommendation created: ID {recommendation.id}")
                            
                    except ValueError:
                        print(f"  ❌ Cannot convert value to float: {value}")
                    except Exception as e:
                        print(f"  ❌ Error creating reading: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"  ❌ Sensor '{sensor_lower}' not recognized")
                    print(f"     Available: {list(sensor_map.keys())}")
            else:
                print(f"  ❌ Sensor or value missing")
        
        print(f"\n📊 FINAL: {created_count} readings added, anomaly: {anomaly_detected}")
        print("="*60)
        
        return Response({
            'status': 'success',
            'message': f'{created_count} reading(s) added',
            'anomaly_detected': anomaly_detected,
            'plot_id': plot_id
        })
        
    except Exception as e:
        print(f"🔥 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# 3. VUES EXISTANTES (INCHANGÉES)
# ============================================================================

class SensorReadingCreateView(generics.CreateAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    permission_classes = [AllowAny]


class SensorReadingListView(generics.ListAPIView):
    queryset = SensorReading.objects.all().order_by("-timestamp")
    serializer_class = SensorReadingSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["plot", "sensor_type"]
    search_fields = ["sensor_type"]
    ordering_fields = ["timestamp", "value"]
    ordering = ["-timestamp"]


class AnomalyEventListView(generics.ListAPIView):
    queryset = AnomalyEvent.objects.all().order_by("-detected_at")
    serializer_class = AnomalyEventSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["plot", "severity"]
    search_fields = ["anomaly_type", "details"]
    ordering_fields = ["detected_at", "severity"]
    ordering = ["-detected_at"]


class AgentRecommendationListView(generics.ListAPIView):
    queryset = AgentRecommendation.objects.all().order_by("-generated_at")
    serializer_class = AgentRecommendationSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["anomaly_event__plot", "confidence"]
    search_fields = ["recommended_action", "explanation_text"]
    ordering_fields = ["generated_at", "confidence"]
    ordering = ["-generated_at"]
