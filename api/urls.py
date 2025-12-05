# api/urls.py
from django.urls import path
from .views import (
    api_root,
    sensor_add,  # <-- AJOUTE CET IMPORT
    SensorReadingCreateView,
    SensorReadingListView,
    AnomalyEventListView,
    AgentRecommendationListView
)

app_name = "api"

urlpatterns = [
    # Vue racine de l'API
    path("", api_root, name="api-root"),
    
    # Batch endpoint pour ajouter plusieurs lectures (NOUVEAU)
    path("sensors/", sensor_add, name="sensor-add"),
    
    # Sensor readings
    path("sensor-readings/create/", SensorReadingCreateView.as_view(), name="sensor-reading-create"),
    path("sensor-readings/", SensorReadingListView.as_view(), name="sensor-reading-list"),

    # Anomalies
    path("anomalies/", AnomalyEventListView.as_view(), name="anomaly-list"),

    # Recommendations
    path("recommendations/", AgentRecommendationListView.as_view(), name="recommendation-list"),
]