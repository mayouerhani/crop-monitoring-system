from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status

from monitoring.models import SensorReading, AnomalyEvent, AgentRecommendation, FieldPlot
from .serializers import (
    SensorReadingSerializer,
    AnomalyEventSerializer,
    AgentRecommendationSerializer
)

# ============================================================================
# 1. VUE RACINE DE L'API
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Page d'accueil de l'API"""
    return Response({
        'project': 'AI-Enhanced Crop Monitoring System',
        'version': '1.0',
        'author': 'Chaouki Bayoudhi',
        'endpoints': {
            'sensor_readings': {
                'create': 'POST /api/sensor-readings/create/',
                'list': 'GET /api/sensor-readings/',
                'filter_examples': [
                    '/api/sensor-readings/?plot=1',
                    '/api/sensor-readings/?sensor_type=soil_moisture'
                ]
            },
            'anomalies': 'GET /api/anomalies/',
            'recommendations': 'GET /api/recommendations/',
            'sensors': 'POST /api/sensors/'
        },
        'note': 'Use the endpoints above to interact with the system'
    })


# ============================================================================
# 2. ENDPOINT BATCH - CORRECTION DES BUGS UNIQUEMENT
# ============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def sensor_add(request):
    """Endpoint batch pour ajouter plusieurs lectures"""
    print("\n" + "="*60)
    print("🔄 sensor_add() CALLED")
    
    try:
        data = request.data
        print(f"📦 Data received: {data}")
        
        plot_id = data.get('plot_id')
        readings = data.get('readings', [])
        
        print(f"📍 plot_id: {plot_id}")
        print(f"📊 readings count: {len(readings)}")
        
        if not plot_id or not readings:
            print("❌ ERROR: plot_id or readings missing")
            return Response(
                {'error': 'plot_id and readings are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Convert plot_id to int
        try:
            plot_id_int = int(plot_id)
        except:
            print(f"❌ Invalid plot_id: {plot_id}")
            return Response(
                {'error': 'plot_id must be a number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifie que le plot existe
        try:
            plot = FieldPlot.objects.get(id=plot_id_int)
            print(f"✅ Plot exists: {plot.name}")
        except FieldPlot.DoesNotExist:
            print(f"❌ Plot {plot_id_int} does not exist")
            return Response(
                {'error': f'Plot {plot_id_int} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Mappage des capteurs - correspond aux SENSOR_TYPES dans models.py
        sensor_map = {
            'moisture': ('moisture', 'percentage'),
            'soil_moisture': ('moisture', 'percentage'),
            'temperature': ('temperature', 'celsius'),
            'air_temperature': ('temperature', 'celsius'),
            'temp': ('temperature', 'celsius'),
            'humidity': ('humidity', 'percentage'),
            'hum': ('humidity', 'percentage'),
            'ph': ('ph', 'ph'),
            'nitrogen': ('nitrogen', 'ppm')
        }
        
        created_count = 0
        anomaly_detected = False
        
        for i, reading in enumerate(readings):
            print(f"\n📝 Processing reading {i}: {reading}")
            
            sensor = reading.get('sensor')
            value = reading.get('value')
            
            print(f"  sensor: '{sensor}'")
            print(f"  value: {value}")
            
            if sensor and value is not None:
                sensor_lower = str(sensor).lower().strip()
                print(f"  sensor_lower: '{sensor_lower}'")
                
                if sensor_lower in sensor_map:
                    print(f"  ✅ Sensor recognized")
                    
                    try:
                        value_float = float(value)
                        
                        # 🔧 BUG FIX: Déstructurer le tuple AVANT create()
                        sensor_type, unit = sensor_map[sensor_lower]
                        
                        # Crée la lecture avec TOUS les champs requis
                        sensor_reading = SensorReading.objects.create(
                            plot=plot,
                            sensor_type=sensor_type,
                            value=value_float,       # 🔧 CORRIGÉ: ce champ manquait!
                            unit=unit
                        )
                        created_count += 1
                        print(f"  ✅ SensorReading created: ID {sensor_reading.id}")
                        
                        # Détection d'anomalie simple
                        if sensor_lower in ['moisture', 'soil_moisture'] and value_float < 30:
                            anomaly_detected = True
                            print(f"  ⚠️ ANOMALY DETECTED: moisture={value_float}")
                            
                            # Crée l'anomalie
                            anomaly = AnomalyEvent.objects.create(
                                plot=plot,
                                anomaly_type='moisture_drop',
                                severity='high',
                                detected_value=value_float,
                                normal_range_min=30,
                                normal_range_max=80,
                                model_confidence=0.9
                            )
                            print(f"  ✅ AnomalyEvent created: ID {anomaly.id}")
                            
                            # Crée la recommandation
                            recommendation = AgentRecommendation.objects.create(
                                anomaly_event=anomaly,
                                recommended_action='irrigation',
                                action_details='Increase irrigation immediately',
                                explanation_text=f'Soil moisture ({value_float}%) is critically low (below 30%)',
                                confidence='high'
                            )
                            print(f"  ✅ AgentRecommendation created: ID {recommendation.id}")
                            
                    except ValueError:
                        print(f"  ❌ Cannot convert value to float: {value}")
                    except Exception as e:
                        print(f"  ❌ Error creating reading: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"  ❌ Sensor '{sensor_lower}' not recognized")
                    print(f"     Available: {list(sensor_map.keys())}")
            else:
                print(f"  ❌ Sensor or value missing")
        
        print(f"\n📊 FINAL: {created_count} readings added, anomaly: {anomaly_detected}")
        print("="*60)
        
        return Response({
            'status': 'success',
            'message': f'{created_count} reading(s) added',
            'anomaly_detected': anomaly_detected,
            'plot_id': plot_id
        })
        
    except Exception as e:
        print(f"🔥 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# 3. VUES EXISTANTES (INCHANGÉES)
# ============================================================================

class SensorReadingCreateView(generics.CreateAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    permission_classes = [AllowAny]


class SensorReadingListView(generics.ListAPIView):
    queryset = SensorReading.objects.all().order_by("-timestamp")
    serializer_class = SensorReadingSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["plot", "sensor_type"]
    search_fields = ["sensor_type"]
    ordering_fields = ["timestamp", "value"]
    ordering = ["-timestamp"]


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
    search_fields = ["anomaly_type", "details"]
    ordering_fields = ["detected_at", "severity"]
    ordering = ["-detected_at"]


class AgentRecommendationListView(generics.ListAPIView):
    queryset = AgentRecommendation.objects.all().order_by("-generated_at")
    serializer_class = AgentRecommendationSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["anomaly_event__plot", "confidence"]
    search_fields = ["recommended_action", "explanation_text"]
    ordering_fields = ["generated_at", "confidence"]
    ordering = ["-generated_at"]