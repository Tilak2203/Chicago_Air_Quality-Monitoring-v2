"""
Airflow-compatible extract step for OpenAQ data.
Fetches the latest hourly measurement from Chicago devices.
Saves raw data to /opt/airflow/dags/data/raw.json
"""

import pandas as pd
from datetime import datetime
from openaq import OpenAQ
from config import OPENAQ_API_KEY
from scripts.preprocess_data import round_df_values, convert_to_datetime
from dateutil import parser

def extract_data():
    """
    Fetch latest hourly Chicago PurpleAir measurements from OpenAQ
    and save them as raw.json for downstream tasks.
    """

    print("🔵 Starting extract_data()")

    # Initialize OpenAQ client
    print("🔵 Initializing OpenAQ client...")
    client = OpenAQ(api_key=OPENAQ_API_KEY)
    device_location = 4903652  # Chicago device ID

    # Fetch latest data
    print(f"🔵 Fetching latest data for device: {device_location}")
    response = client.locations.latest(device_location)

    print("🔵 Raw API response:")
    print(response)

    # Extract sensor readings
    print("🔵 Extracting sensor readings...")
    sensor_readings = {}
    for item in response.results:
        sensor_readings[item.sensors_id] = item.value
    
    print("🔵 Sensor readings extracted:")
    print(sensor_readings)

    # Convert timestamp to datetime
    utc = parser.isoparse(item.datetime["utc"])

    utc_str = item.datetime["utc"]
    print("BOT")
    if utc_str.endswith('Z'):
        utc_str = utc_str[:-1] + '+00:00'
    utc = datetime.fromisoformat(utc_str)
    print("🔵 Parsed timestamp:", utc)   

    # Create dataframe
    df = pd.DataFrame([{
        "timestamp": utc,
        "pm1 (µg/m³)": sensor_readings.get(13477544),
        "pm25 (µg/m³)": sensor_readings.get(13477545),
        "Relative Humidity (%)": sensor_readings.get(13477546),
        "Temperature (c)": sensor_readings.get(13477547),
        "pm03 (µg/m³)": sensor_readings.get(13477548),
    }])
    
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)

    print("Raw dataframe BEFORE cleaning:")
    print(df)

    # Light cleanup
    df = round_df_values(df)
    df = convert_to_datetime(df)

    print("🔵 Dataframe AFTER cleaning:")
    print(df)

    output_path = "/opt/airflow/dags/data/raw.json"
    df.to_json(output_path, orient="records", default_handler=str)

    print(f"🟢 Saved raw data to {output_path}")
    return output_path


# sys.path.append("/opt/airflow/dags")
# sys.path.append("/opt/airflow/dags/scripts")