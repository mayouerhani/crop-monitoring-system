from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class FarmProfile(models.Model):
    FARM_TYPES = [
        ('organic', 'Organic'),
        ('conventional', 'Conventional'),
        ('hydroponic', 'Hydroponic'),
        ('greenhouse', 'Greenhouse'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Size in hectares")
    farm_type = models.CharField(max_length=20, choices=FARM_TYPES, default='conventional')
    soil_type = models.CharField(max_length=100)
    established_date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'farm_profile'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['owner']),
        ]
        verbose_name = 'Farm Profile'
        verbose_name_plural = 'Farm Profiles'

    def __str__(self):
        return f'{self.name} - {self.location}'

class FieldPlot(models.Model):
    CROP_TYPES = [
        ('wheat', 'Wheat'),
        ('corn', 'Corn'),
        ('soybean', 'Soybean'),
        ('rice', 'Rice'),
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
    ]
    
    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='plots')
    name = models.CharField(max_length=255)
    crop_type = models.CharField(max_length=20, choices=CROP_TYPES)
    crop_variety = models.CharField(max_length=100)
    size = models.DecimalField(max_digits=8, decimal_places=2, help_text="Size in hectares")
    planting_date = models.DateField()
    expected_harvest_date = models.DateField()
    location_coordinates = models.CharField(max_length=255, blank=True, null=True)
    irrigation_system = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'field_plot'
        ordering = ['farm', 'name']
        indexes = [
            models.Index(fields=['farm', 'name']),
            models.Index(fields=['crop_type']),
        ]
        verbose_name = 'Field Plot'
        verbose_name_plural = 'Field Plots'

    def __str__(self):
        return f'{self.name} - {self.crop_type}'

class SensorReading(models.Model):
    SENSOR_TYPES = [
        ('moisture', 'Soil Moisture'),
        ('temperature', 'Air Temperature'),
        ('humidity', 'Humidity'),
        ('ph', 'pH Level'),
        ('nitrogen', 'Nitrogen Level'),
    ]
    
    UNITS = [
        ('percentage', '%'),
        ('celsius', '°C'),
        ('fahrenheit', '°F'),
        ('ph', 'pH'),
        ('ppm', 'PPM'),
    ]
    
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name='sensor_readings')
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPES)
    value = models.DecimalField(max_digits=8, decimal_places=3)
    unit = models.CharField(max_length=20, choices=UNITS)
    timestamp = models.DateTimeField(auto_now_add=True)
    sensor_id = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    class Meta:
        db_table = 'sensor_reading'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['plot', 'timestamp']),
            models.Index(fields=['sensor_type', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
        verbose_name = 'Sensor Reading'
        verbose_name_plural = 'Sensor Readings'

    def __str__(self):
        return f'{self.plot.name} - {self.sensor_type}: {self.value}'

class AnomalyEvent(models.Model):
    ANOMALY_TYPES = [
        ('moisture_drop', 'Soil Moisture Drop'),
        ('temperature_spike', 'Temperature Spike'),
        ('humidity_anomaly', 'Humidity Anomaly'),
        ('ph_imbalance', 'pH Imbalance'),
        ('nutrient_deficiency', 'Nutrient Deficiency'),
        ('pest_infestation', 'Pest Infestation'),
        ('disease_detection', 'Disease Detection'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name='anomalies')
    anomaly_type = models.CharField(max_length=50, choices=ANOMALY_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    detected_value = models.DecimalField(max_digits=8, decimal_places=3)
    normal_range_min = models.DecimalField(max_digits=8, decimal_places=3)
    normal_range_max = models.DecimalField(max_digits=8, decimal_places=3)
    model_confidence = models.DecimalField(max_digits=5, decimal_places=3, help_text="Confidence score from 0 to 1")
    detected_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'anomaly_event'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['plot', 'detected_at']),
            models.Index(fields=['severity', 'is_resolved']),
            models.Index(fields=['anomaly_type']),
        ]
        verbose_name = 'Anomaly Event'
        verbose_name_plural = 'Anomaly Events'

    def __str__(self):
        return f'{self.plot.name} - {self.anomaly_type} ({self.severity})'

class AgentRecommendation(models.Model):
    CONFIDENCE_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    ACTION_TYPES = [
        ('irrigation', 'Adjust Irrigation'),
        ('fertilization', 'Apply Fertilizer'),
        ('pest_control', 'Pest Control'),
        ('disease_treatment', 'Disease Treatment'),
        ('harvest', 'Schedule Harvest'),
        ('monitoring', 'Increase Monitoring'),
        ('consultation', 'Consult Expert'),
    ]
    
    anomaly_event = models.OneToOneField(
        AnomalyEvent, 
        on_delete=models.CASCADE, 
        related_name='recommendation'
    )
    recommended_action = models.CharField(max_length=50, choices=ACTION_TYPES)
    action_details = models.TextField()
    explanation_text = models.TextField()
    confidence = models.CharField(max_length=20, choices=CONFIDENCE_LEVELS)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_duration = models.CharField(max_length=100, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_implemented = models.BooleanField(default=False)
    implemented_at = models.DateTimeField(null=True, blank=True)
    implementation_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'agent_recommendation'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['anomaly_event']),
            models.Index(fields=['is_implemented']),
        ]
        verbose_name = 'Agent Recommendation'
        verbose_name_plural = 'Agent Recommendations'

    def __str__(self):
        return f'Recommendation for {self.anomaly_event.plot.name}'

# Additional models for comprehensive crop monitoring

class WeatherData(models.Model):
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name='weather_data')
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.DecimalField(max_digits=5, decimal_places=2)
    rainfall = models.DecimalField(max_digits=6, decimal_places=2, help_text="Rainfall in mm")
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2)
    solar_radiation = models.DecimalField(max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField()
    
    class Meta:
        db_table = 'weather_data'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['plot', 'timestamp']),
        ]
        verbose_name = 'Weather Data'
        verbose_name_plural = 'Weather Data'

class IrrigationLog(models.Model):
    IRRIGATION_TYPES = [
        ('drip', 'Drip Irrigation'),
        ('sprinkler', 'Sprinkler System'),
        ('flood', 'Flood Irrigation'),
        ('manual', 'Manual Watering'),
    ]
    
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name='irrigation_logs')
    irrigation_type = models.CharField(max_length=20, choices=IRRIGATION_TYPES)
    water_volume = models.DecimalField(max_digits=8, decimal_places=2, help_text="Water volume in liters")
    duration_minutes = models.PositiveIntegerField()
    irrigated_at = models.DateTimeField()
    moisture_before = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    moisture_after = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'irrigation_log'
        ordering = ['-irrigated_at']
        indexes = [
            models.Index(fields=['plot', 'irrigated_at']),
        ]
        verbose_name = 'Irrigation Log'
        verbose_name_plural = 'Irrigation Logs'

class HarvestRecord(models.Model):
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name='harvest_records')
    harvest_date = models.DateField()
    yield_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Yield in kg")
    quality_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Quality rating from 1 to 10"
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'harvest_record'
        ordering = ['-harvest_date']
        indexes = [
            models.Index(fields=['plot', 'harvest_date']),
        ]
        verbose_name = 'Harvest Record'
        verbose_name_plural = 'Harvest Records'
from django.db import models
from django.contrib.auth.models import User

# Keep existing Plot model if it exists, if not add:
class Plot(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plots')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    crop_type = models.CharField(max_length=100)
    size = models.FloatField(help_text="Size in hectares")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.crop_type})"


class SensorReading(models.Model):
    SENSOR_TYPES = [
        ('temperature', 'Temperature (°C)'),
        ('humidity', 'Humidity (%)'),
        ('soil_moisture', 'Soil Moisture (%)'),
        ('ph_level', 'pH Level'),
        ('light_intensity', 'Light Intensity (lux)'),
    ]
    
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='sensor_readings')
    sensor_type = models.CharField(max_length=50, choices=SENSOR_TYPES)
    value = models.FloatField()
    unit = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['plot', 'sensor_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.plot.name} - {self.sensor_type}: {self.value}"


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    ALERT_TYPES = [
        ('temperature', 'Temperature'),
        ('humidity', 'Humidity'),
        ('soil_moisture', 'Soil Moisture'),
        ('ph_level', 'pH Level'),
        ('light_intensity', 'Light Intensity'),
    ]
    
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, db_index=True)
    message = models.TextField()
    current_value = models.FloatField()
    threshold_value = models.FloatField()
    recommendations = models.JSONField(default=list, blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['plot', '-timestamp']),
            models.Index(fields=['severity', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.plot.name} - {self.alert_type} ({self.severity})"


class AlertHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('viewed', 'Viewed'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]
    
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']