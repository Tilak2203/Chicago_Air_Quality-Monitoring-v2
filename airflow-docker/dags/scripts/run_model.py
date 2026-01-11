"""
Run ML model on new clean data and insert prediction into MongoDB.
"""

import pandas as pd
import joblib
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from config import MONGODB_URI

MODEL_PATH = "/opt/airflow-docker/include/models/RandForestModel.pkl"

def run_model():
    # Connect to DB
    client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
    db = client["air_quality"]
    measurements = db["measurements"]
    predictions = db["predictions"]

    # Load latest clean data
    df = pd.read_json("/opt/airflow/dags/data/clean.json")
    if df.empty:
        print("No data for prediction.")
        return

    latest = df.iloc[-1]

    # Load model
    model = joblib.load(MODEL_PATH)

    feature_cols = [
        "pm1 (µg/m³)",
        "Relative Humidity (%)",
        "Temperature (c)",
        "pm03 (µg/m³)",
        "hour",
        "day_of_week",
        "month"
    ]

    X = latest[feature_cols].values.reshape(1, -1)
    pred = float(model.predict(X)[0])
    pred = round(pred, 2)

    predictions.insert_one({
        "timestamp": latest["timestamp"],
        "predicted_pm25": pred
    })

    print(f"Predicted PM2.5 = {pred}")
    return pred
