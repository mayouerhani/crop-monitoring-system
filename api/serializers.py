from rest_framework import serializers
from monitoring.models import FarmProfile, FieldPlot, SensorReading, AnomalyEvent, AgentRecommendation, WeatherData, IrrigationLog, HarvestRecord

class FarmProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmProfile
        fields = '__all__'

class FieldPlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldPlot
        fields = '__all__'

class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = '__all__'

class AnomalyEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnomalyEvent
        fields = '__all__'

class AgentRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentRecommendation
        fields = '__all__'

class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = '__all__'

class IrrigationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IrrigationLog
        fields = '__all__'

class HarvestRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HarvestRecord
        fields = '__all__'
from rest_framework import serializers
from monitoring.models import Plot, SensorReading, Alert, AlertHistory


class PlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plot
        fields = ['id', 'name', 'description', 'location', 'crop_type', 'size', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = ['id', 'plot', 'sensor_type', 'value', 'unit', 'timestamp']
        read_only_fields = ['timestamp']


class AlertHistorySerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = AlertHistory
        fields = ['id', 'action', 'user_email', 'notes', 'timestamp']
        read_only_fields = ['timestamp']


class AlertDetailSerializer(serializers.ModelSerializer):
    plot_name = serializers.CharField(source='plot.name', read_only=True)
    history = AlertHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'plot', 'plot_name', 'alert_type', 'severity', 'message',
            'current_value', 'threshold_value', 'recommendations', 
            'is_resolved', 'resolved_at', 'timestamp', 'history'
        ]
        read_only_fields = ['timestamp', 'resolved_at']


class AlertSerializer(serializers.ModelSerializer):
    plot_name = serializers.CharField(source='plot.name', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'plot', 'plot_name', 'alert_type', 'severity', 'message',
            'current_value', 'threshold_value', 'recommendations',
            'is_resolved', 'timestamp'
        ]
        read_only_fields = ['timestamp']