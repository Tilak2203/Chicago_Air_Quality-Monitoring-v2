import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from config import MONGODB_URI
from datetime import datetime, timedelta
import json
import sys
from datetime import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

MODEL_PATH = Path(__file__).parent / "RandForestModel.pkl"

uri = MONGODB_URI
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["air_quality"]
collection = db['measurements']
predictions_collection = db["predictions"] 

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!", file=sys.stderr)
except Exception as e:
    print(f"MongoDB connection error: {e}", file=sys.stderr)


def predict_pm25():
    try:
        # Get latest document
        latest_doc = collection.find_one(sort=[("timestamp", -1)])

        if not latest_doc:
            print("No data available for prediction")
            return None

        # Load model
        with open(MODEL_PATH, 'rb') as f:
            RandForestModel = pickle.load(f)

        # Prepare features
        feature_cols = [
            "pm1 (µg/m³)",
            "Relative Humidity (%)",
            "Temperature (c)",
            "pm03 (µg/m³)",
            "hour",
            "day_of_week",
            "month"
        ]

        # Check if all required features exist
        missing_features = [col for col in feature_cols if col not in latest_doc]
        if missing_features:
            print(f"Missing features: {missing_features}")
            return None

        # Create feature vector
        X = pd.DataFrame([latest_doc])[feature_cols]

        # Make prediction
        y_pred = RandForestModel.predict(X)[0]
        predicted_value = round(float(y_pred), 1)

        print(f"Predicted PM2.5 for next hour: {predicted_value}")

        return predicted_value

    except Exception as e:
        print(f"Prediction failed: {e}")
        return None