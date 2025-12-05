from django.urls import path
from monitoring.views import add_sensor_readings

urlpatterns = [
    path('sensors/', add_sensor_readings, name='sensor-add'),
]
