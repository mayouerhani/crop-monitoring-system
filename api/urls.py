from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, SensorReadingAnalysisViewSet, PlotViewSet

router = DefaultRouter()
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'plots', PlotViewSet, basename='plot')
router.register(r'analysis', SensorReadingAnalysisViewSet, basename='analysis')

urlpatterns = [
    path('', include(router.urls)),
]