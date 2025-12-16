from rest_framework.decorators import api_view
from rest_framework.response import Response
from monitoring.models import FieldPlot, SensorReading, AnomalyEvent, AgentRecommendation
from monitoring.ml import detect_anomalies
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny




@api_view(['POST'])
@permission_classes([AllowAny])
def add_sensor_readings(request):
    """
    Exemple JSON POST :
    {
        "plot_id": 1,
        "moisture": 55.2,
        "temperature": 24.7,
        "humidity": 60.1
    }
    """

    data = request.data

    # --- 1. Vérification ---
    if not all(key in data for key in ['plot_id', 'moisture', 'temperature', 'humidity']):
        return Response({"error": "Missing fields"}, status=400)

    plot = FieldPlot.objects.get(id=data['plot_id'])

    moisture = float(data['moisture'])
    temp = float(data['temperature'])
    hum = float(data['humidity'])

    # --- 2. Stocker lecture dans SensorReading ---
    SensorReading.objects.create(
        field_plot=plot,
        value=moisture,         # tu peux changer dans ton modèle plus tard
        timestamp=None          # Django met auto_now_add si configuré
    )

    # --- 3. Préparer données vers ML ---
    ml_input = [[moisture, temp, hum]]   # format attendu par detect_anomalies()

    predictions = detect_anomalies(ml_input)

    is_anomaly = (predictions[0] == -1)

    # --- 4. Enregistrer une anomalie ---
    if is_anomaly:
        anomaly = AnomalyEvent.objects.create(
            field_plot=plot,
            description=f"Anomaly detected: moisture={moisture} temp={temp} hum={hum}",
        )

        AgentRecommendation.objects.create(
            field_plot=plot,
            message="⚠️ Check this plot. ML model detected unusual sensor behavior.",
        )

    # --- 5. Réponse JSON ---
    return Response({
        "status": "success",
        "is_anomaly": is_anomaly
    })
