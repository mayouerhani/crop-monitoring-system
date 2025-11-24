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