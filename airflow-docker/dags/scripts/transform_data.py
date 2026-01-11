"""
Airflow transform step.
Loads raw.json → preprocess → save to clean.json
"""

import pandas as pd
import json
from scripts.preprocess_data import (
    convert_to_datetime,
    round_df_values,
    remove_outliers_csv
)

def transform_data():
    input_path = "/opt/airflow/dags/data/raw.json"
    output_path = "/opt/airflow/dags/data/clean.json"

    df = pd.read_json(input_path)

    # Basic cleaning
    df = round_df_values(df)
    df = convert_to_datetime(df)

    # Remove outliers
    df = remove_outliers_csv(df, "pm25 (µg/m³)")

    df['timestamp'] = df['timestamp'].dt.strftime("%Y-%m-%d %H:%M:%S")

    df.to_csv("/opt/airflow/dags/data/clean.csv", index=False)
    print(df.head())
    print(f"Saved clean data to {output_path}")

    return output_path
