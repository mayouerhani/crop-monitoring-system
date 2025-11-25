from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from monitoring.models import SensorReading, AnomalyEvent, AgentRecommendation
from .serializers import (
    SensorReadingSerializer,
    AnomalyEventSerializer,
    AgentRecommendationSerializer
)


# POST /api/sensor-readings/create/

class SensorReadingCreateView(generics.CreateAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    permission_classes = [AllowAny]  # tu peux mettre IsAuthenticated



# GET /api/sensor-readings/

class SensorReadingListView(generics.ListAPIView):
    queryset = SensorReading.objects.all().order_by("-timestamp")
    serializer_class = SensorReadingSerializer
    permission_classes = [AllowAny]

    # Activation des filtres DRF
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # 🔍 Filtres disponibles dans l’URL
    filterset_fields = ["plot", "sensor_type"]

    # 🔎 Search /api/sensor-readings/?search=temperature
    search_fields = ["sensor_type"]

    # ↕ Ordering /api/sensor-readings/?ordering=timestamp
    ordering_fields = ["timestamp", "soil_moisture", "temperature"]
    ordering = ["-timestamp"]



# 3. LIST ANOMALY EVENTS

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
    search_fields = ["description"]
    ordering_fields = ["detected_at", "severity"]
    ordering = ["-detected_at"]



# 4. LIST RECOMMENDATIONS

class AgentRecommendationListView(generics.ListAPIView):
    queryset = AgentRecommendation.objects.all().order_by("-generated_at")
    serializer_class = AgentRecommendationSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["plot", "category"]
    search_fields = ["action_text"]
    ordering_fields = ["generated_at"]
    ordering = ["-generated_at"]
