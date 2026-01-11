from flask import Flask, jsonify, request
from flask_cors import CORS
import mongodb 
import subprocess
import json
import sys
from pathlib import Path
from predict import predict_pm25
from pymongo import MongoClient
from config import MONGODB_URI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

uri = MONGODB_URI

client = MongoClient(uri, server_api=ServerApi('1'))
db = client["air_quality"]
collection = db['measurements']

# Load your trained model (update path if different)
MODEL_PATH = Path(__file__).parent / "RandForestModel.pkl"
model = joblib.load(MODEL_PATH)


@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello World from backend!"})

@app.route('/api/status')
def status():
    mongodb_connected = mongodb.get_connection_status()
    return jsonify({
        "mongodb_connected": mongodb_connected,
        "status": "ok" if mongodb_connected else "error"
    })
    
# @app.route('/api/all-readings')
# def all_readings():
#     data = mongodb.get_all_readings()
#     return jsonify({
#         "readings": data,
#         "count": len(data),
#         "start_date": data[0]["timestamp"] if data else None,
#         "end_date": data[-1]["timestamp"] if data else None
#     })

@app.route("/api/all-readings", methods=["GET"])
def api_all_readings():
    try:
        # Get raw readings (MongoDB or CSV)
        readings = mongodb.get_all_readings()
        print
        if not readings:
            return jsonify({"readings": []})

        df = pd.DataFrame(readings)

        # Ensure timestamp column exists
        if "timestamp" not in df.columns:
            return jsonify({"readings": []})

        # Convert ANY timestamp input into datetime safely:
        # - string timestamps
        # - Unix ints (1704979200)
        # - datetime objects
        # - None values
        def clean_ts(x):
            try:
                # If numeric (int/float), treat as UNIX timestamp
                if isinstance(x, (int, float)):
                    return pd.to_datetime(int(x), unit="s")
                return pd.to_datetime(x, errors="coerce")
            except:
                return None

        df["timestamp"] = df["timestamp"].apply(clean_ts)

        # Drop bad timestamps
        df = df.dropna(subset=["timestamp"])

        # Sort safely now that everything is datetime
        df = df.sort_values(by="timestamp")

        # Convert to ISO for React compatibility
        df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S")

        # Convert to JSON-safe format
        return jsonify({"readings": df.to_dict(orient="records")})

    except Exception as e:
        print("Error retrieving data:", e)
        return jsonify({"readings": [], "error": str(e)}), 500


@app.route('/api/predict', methods=['POST'])
def predict_route():
    try:
        predicted_value = predict_pm25()  
        if predicted_value is None:
            return jsonify({
                "error": "Prediction failed",
                "success": False
            }), 500

        return jsonify({
            "predicted_pm25": predicted_value,
            "success": True
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "success": False
        }), 500
        
    
@app.route('/api/prediction-history', methods=['GET'])
def prediction_history():
    try:
        # Get last 5 rows, sorted by timestamp (descending)
        last_rows = list(
            collection.find({}, {"_id": 0})  # exclude _id
            .sort("timestamp", -1)
            .limit(5)
        )

        results = []
        for row in last_rows:
            actual = row.get("pm25 (µg/m³)", None)
            timestamp = row.get("timestamp")

            # Use the features your model was trained on
            features = [[
                row.get("pm1 (µg/m³)"),
                row.get("Relative Humidity (%)"),
                row.get("Temperature (c)"),
                row.get("pm03 (µg/m³)"),
                row.get("hour"),
                row.get("day_of_week"),
                row.get("month")
            ]]

            predicted = float(model.predict(features)[0])
            
            # print(f"Timestamp: {timestamp}")
            # print(f"Features: {features}")
            # print(f"Actual: {actual}")
            # print(f"Predicted: {predicted}")
            
            results.append({
                "timestamp": timestamp, 
                "actual": round(actual, 2) if actual is not None else None,
                "predicted": round(predicted, 2)
            })

        return jsonify({"success": True, "data": results})  # reverse to chronological order

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/model-metrics', methods=['GET'])
def model_metrics():
    try:
        # Fetch last N rows for evaluation (adjust N as needed)
        N = 100
        rows = list(
            collection.find({}, {"_id": 0})
            .sort("timestamp", -1)
            .limit(N)
        )
        if not rows:
            return jsonify({"success": False, "error": "No data for evaluation"})

        # Prepare features & targets
        X = []
        y_true = []
        for row in rows:
            # Only use rows with all required features present
            features = [
                row.get("pm1 (µg/m³)"),
                row.get("Relative Humidity (%)"),
                row.get("Temperature (c)"),
                row.get("pm03 (µg/m³)"),
                row.get("hour"),
                row.get("day_of_week"),
                row.get("month")
            ]
            if None not in features and row.get("pm25 (µg/m³)") is not None:
                X.append(features)
                y_true.append(row["pm25 (µg/m³)"])
        if not X:
            return jsonify({"success": False, "error": "No valid data for evaluation"})

        # Predict
        y_pred = model.predict(X)

        # Compute metrics
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

        mae = mean_absolute_error(y_true, y_pred)
        rmse = mean_squared_error(y_true, y_pred) ** 0.5
        r2 = r2_score(y_true, y_pred)

        return jsonify({
            "success": True,
            "metrics": {
                "mae": round(mae, 2),
                "rmse": round(rmse, 2),
                "r2": round(r2, 3)
            },
            "n_samples": len(y_true)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
