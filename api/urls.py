
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, SensorReadingAnalysisViewSet, PlotViewSet

router = DefaultRouter()
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'plots', PlotViewSet, basename='plot')
router.register(r'analysis', SensorReadingAnalysisViewSet, basename='analysis')

urlpatterns = [
    path('', include(router.urls)),]
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