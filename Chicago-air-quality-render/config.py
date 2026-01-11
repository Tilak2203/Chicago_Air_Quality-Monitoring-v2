import os

OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "06319710ff4c0ef3acbd8058a8f529333d856419ab6819f22ccf04d002fe0430")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://tilak:tilak@airquality.tcaneue.mongodb.net/?retryWrites=true&w=majority&appName=AirQuality")

DEFAULT_COORDINATES = [41.893333, -87.634176]

DEFAULT_RADIUS = 1000 

SENSOR_IDS = {
    "pm1": 13477544,
    "pm25": 13477545,
    "rh": 13477546,
    "temp": 13477547,
    "pm03": 13477548,
}

# # config.py
# import os
# import json

# # MongoDB and API key
# MONGODB_URI = os.environ.get("MONGODB_URI")
# OPENAQ_API_KEY = os.environ.get("OPENAQ_API_KEY")

# # Default values
# DEFAULT_COORDINATES = json.loads(os.environ.get("DEFAULT_COORDINATES", "[41.893333, -87.634176]"))
# DEFAULT_RADIUS = int(os.environ.get("DEFAULT_RADIUS", "1000"))

# # Sensor IDs (stored as JSON in env variable)
# SENSOR_IDS = json.loads(os.environ.get("SENSOR_IDS", "{}"))


