import os
import pickle
import pandas as pd
from sklearn.ensemble import IsolationForest

MODEL_FILE = 'isolation_model.pkl'

def load_model():
    if os.path.exists(MODEL_FILE):
        with open(MODEL_FILE,'rb') as f:
            return pickle.load(f)
    return None

def train_model(sensor_data):
    df = pd.DataFrame(sensor_data, columns=['moisture','temp','hum'])
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(df)
    with open(MODEL_FILE,'wb') as f:
        pickle.dump(model,f)
    return model

def detect_anomalies(sensor_data, model=None):
    if model is None:
        model = load_model()
    if model is None:
        raise ValueError("No model available")
    df = pd.DataFrame(sensor_data, columns=['moisture','temp','hum'])
    predictions = model.predict(df)
    return predictions  # 1=normal, -1=anomaly
