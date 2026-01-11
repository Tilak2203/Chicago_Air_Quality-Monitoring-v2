from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import pandas as pd
import numpy as np
import seaborn as sns
from config import MONGODB_URI

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

from preprocess_data import scale_data

import pickle


uri = MONGODB_URI
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
def train_and_save():
    db = client["air_quality"]
    collection = db['measurements']
    cursor = collection.find({}).sort("timestamp", 1)  # sort by time
    data = list(cursor)

    for row in data:
        row.pop('_id', None)

    # Convert to pandas DataFrame
    df = pd.DataFrame(data)
    df = df.sort_values("timestamp")  # ensure chronological order

    # Shift target column to create "next hour" label
    df["pm25_next_hour"] = df["pm25 (µg/m³)"].shift(-1)

    # Drop last row (since it has no "next hour" target)
    df = df.dropna()

    # df = scale_data(df)

    print(df.head())

    # Features: current readings (except timestamp and target columns)
    X = df.drop(columns=['pm25 (µg/m³)', 'timestamp', 'pm25_next_hour'], axis=1)
    y = df['pm25_next_hour']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False  # no shuffling, keep time order
    )

    RandForestModel = RandomForestRegressor(n_estimators=100, random_state=42)
    RandForestModel.fit(X_train, y_train)

    y_pred = RandForestModel.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Next-Hour Prediction MSE: {mse:.2f}")
    
    print(df.head())

    results_df = pd.DataFrame({'Actual_NextHour': y_test.values, 'Predicted_NextHour': y_pred})
    print("\nFirst 5 Actual vs Predicted Next Hour values:")
    print(results_df.head())
    
    with open('RandForestModel.pkl', 'wb') as f:
        pickle.dump(RandForestModel, f)
    print("Next-hour model saved to RandForestModel.pkl")

def train_and_save_lr():
    db = client["air_quality"]
    collection = db['measurements']
    cursor = collection.find({}).sort("timestamp", 1)  # sort by time
    data = list(cursor)

    for row in data:
        row.pop('_id', None)

    # Convert to pandas DataFrame
    df = pd.DataFrame(data)
    df = df.sort_values("timestamp")  # ensure chronological order

    # Shift target column to create "next hour" label
    df["pm25_next_hour"] = df["pm25 (µg/m³)"].shift(-1)

    # Drop last row (since it has no "next hour" target)
    df = df.dropna()

    # Features: current readings (except timestamp and target columns)
    X = df.drop(columns=['pm25 (µg/m³)', 'timestamp', 'pm25_next_hour'], axis=1)
    y = df['pm25_next_hour']

    # Train/test split (no shuffle, keep time order)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    # Linear Regression model
    from sklearn.linear_model import LinearRegression
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)

    # Predictions
    y_pred = lr_model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Next-Hour Prediction MSE (Linear Regression): {mse:.2f}")

    # Show sample predictions
    results_df = pd.DataFrame({'Actual_NextHour': y_test.values, 'Predicted_NextHour': y_pred})
    print("\nFirst 5 Actual vs Predicted Next Hour values (Linear Regression):")
    print(results_df.head())

    # Save model
    with open('LinearRegressionModel.pkl', 'wb') as f:
        pickle.dump(lr_model, f)
    print("Next-hour Linear Regression model saved to LinearRegressionModel.pkl")


if __name__ == "__main__":
    train_and_save()
    # train_and_save_lr()
    