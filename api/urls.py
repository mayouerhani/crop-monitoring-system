from django.urls import path
from .views import (
    SensorReadingCreateView,
    SensorReadingListView,
    AnomalyEventListView,
    AgentRecommendationListView
)

app_name = "api"

urlpatterns = [
    # Sensor readings
    path("sensor-readings/create/", SensorReadingCreateView.as_view(), name="sensor-reading-create"),
    path("sensor-readings/", SensorReadingListView.as_view(), name="sensor-reading-list"),

    # Anomalies
    path("anomalies/", AnomalyEventListView.as_view(), name="anomaly-list"),

    # Recommendations
    path("recommendations/", AgentRecommendationListView.as_view(), name="recommendation-list"),
]
