from django.contrib import admin
from .models import FarmProfile, FieldPlot, SensorReading, AnomalyEvent, AgentRecommendation, WeatherData, IrrigationLog, HarvestRecord

@admin.register(FarmProfile)
class FarmProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'location', 'farm_type', 'size']
    list_filter = ['farm_type', 'soil_type']
    search_fields = ['name', 'location']

@admin.register(FieldPlot)
class FieldPlotAdmin(admin.ModelAdmin):
    list_display = ['name', 'farm', 'crop_type', 'crop_variety', 'planting_date']
    list_filter = ['crop_type', 'farm']
    search_fields = ['name', 'crop_variety']

@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['plot', 'sensor_type', 'value', 'unit', 'timestamp']
    list_filter = ['sensor_type', 'timestamp']
    search_fields = ['plot__name']

@admin.register(AnomalyEvent)
class AnomalyEventAdmin(admin.ModelAdmin):
    list_display = ['plot', 'anomaly_type', 'severity', 'detected_at', 'is_resolved']
    list_filter = ['anomaly_type', 'severity', 'is_resolved']
    search_fields = ['plot__name']

@admin.register(AgentRecommendation)
class AgentRecommendationAdmin(admin.ModelAdmin):
    list_display = ['anomaly_event', 'recommended_action', 'confidence', 'is_implemented']
    list_filter = ['recommended_action', 'confidence', 'is_implemented']

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['plot', 'temperature', 'humidity', 'rainfall', 'timestamp']
    list_filter = ['timestamp']

@admin.register(IrrigationLog)
class IrrigationLogAdmin(admin.ModelAdmin):
    list_display = ['plot', 'irrigation_type', 'water_volume', 'irrigated_at']
    list_filter = ['irrigation_type']

@admin.register(HarvestRecord)
class HarvestRecordAdmin(admin.ModelAdmin):
    list_display = ['plot', 'harvest_date', 'yield_amount', 'quality_rating']
    list_filter = ['harvest_date']