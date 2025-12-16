from django.core.management.base import BaseCommand
from monitoring.models import FieldPlot, SensorReading, AnomalyEvent, AgentRecommendation
import time
import random
from datetime import datetime, timedelta
import pandas as pd
from sklearn.ensemble import IsolationForest
import os
import pickle
import math

MODEL_FILE = 'isolation_model.pkl'

class Command(BaseCommand):
    help = 'Run advanced crop simulator with anomaly injection and ML detection'

    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, default=5)
        parser.add_argument('--duration', type=int, default=0)
        parser.add_argument('--plots', type=int, default=1)

    def handle(self, *args, **options):
        interval = options['interval']
        duration = options['duration']
        num_plots = options['plots']

        self.stdout.write(self.style.SUCCESS(f'Starting simulation for {num_plots} plot(s)'))

        plots = FieldPlot.objects.all()[:num_plots]
        if not plots:
            self.stdout.write(self.style.ERROR('No FieldPlot found'))
            return

        # Charger ou créer IsolationForest
        if os.path.exists(MODEL_FILE):
            with open(MODEL_FILE, 'rb') as f:
                iso_model = pickle.load(f)
            self.stdout.write('IsolationForest model loaded.')
        else:
            iso_model = None
            self.stdout.write('No model found, will train after first batch.')

        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=duration) if duration > 0 else None
        time_step = 0

        while True:
            batch_data = []
            batch_readings = []

            for plot in plots:
                # Patterns réalistes
                moisture = round(50 + 10*math.sin(time_step/5) + random.uniform(-5,5),2)
                temp = round(25 + 5*math.sin(time_step/10) + random.uniform(-2,2),2)
                hum = round(60 + 10*math.sin(time_step/7) + random.uniform(-5,5),2)

                # Injection d'anomalies ponctuelles
                if time_step % 10 == 0:  # toutes les 10 itérations
                    moisture = random.choice([20,85])
                    temp = random.choice([10,40])

                # Créer SensorReadings
                for sensor_type, value, unit in [
                    ('moisture', moisture, 'percentage'),
                    ('temperature', temp, 'celsius'),
                    ('humidity', hum, 'percentage')
                ]:
                    SensorReading.objects.create(
                        plot=plot,
                        sensor_type=sensor_type,
                        value=value,
                        unit=unit,
                        timestamp=datetime.now()
                    )

                self.stdout.write(f'[SIM] {plot.name} -> moisture={moisture} temp={temp} hum={hum}')
                batch_data.append([moisture,temp,hum])
                batch_readings.append(plot)

            # Entraîner IsolationForest si pas encore fait
            if iso_model is None and len(batch_data) >= 5:
                df_train = pd.DataFrame(batch_data, columns=['moisture','temp','hum'])
                iso_model = IsolationForest(contamination=0.05, random_state=42)
                iso_model.fit(df_train)
                with open(MODEL_FILE,'wb') as f:
                    pickle.dump(iso_model,f)
                self.stdout.write(self.style.SUCCESS('IsolationForest trained and saved.'))

            # Détection des anomalies
            if iso_model:
                df_batch = pd.DataFrame(batch_data, columns=['moisture','temp','hum'])
                predictions = iso_model.predict(df_batch)
                for i,pred in enumerate(predictions):
                    if pred==-1:
                        anomaly = AnomalyEvent.objects.create(
                            plot=batch_readings[i],
                            anomaly_type='moisture_drop',
                            severity='high',
                            detected_value=batch_data[i][0],
                            normal_range_min=40,
                            normal_range_max=80,
                            model_confidence=0.9,
                            description=f'Anomalous reading detected: {batch_data[i]}'
                        )
                        AgentRecommendation.objects.create(
                            anomaly_event=anomaly,
                            recommended_action='monitoring',
                            action_details='Increase monitoring of soil moisture',
                            explanation_text='Anomaly detected by IsolationForest',
                            confidence='high'
                        )
                        self.stdout.write(f'[ML] Anomaly created: {anomaly.description} / Recommendation created.')

            time_step += 1
            if end_time and datetime.now() >= end_time:
                self.stdout.write(self.style.SUCCESS('Simulation finished (duration reached).'))
                break

            time.sleep(interval)
