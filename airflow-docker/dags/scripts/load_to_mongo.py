"""
Loads clean processed data into MongoDB.
"""


import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from config import MONGODB_URI

def load_to_mongo():
    client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
    db = client["air_quality"]
    collection = db["measurements"]

    try:
        client.admin.command("ping")
        print("Connected to MongoDB Atlas!")
    except Exception as e:
        print("Mongo connection error:", e)
        return

    input_path = "/opt/airflow/dags/data/clean.csv"
    df = pd.read_csv(input_path, parse_dates=["timestamp"])

    print("Data going into MongoDB:")
    print(df)

    docs = df.to_dict("records")

    for doc in docs:
    # Force timestamp to match previous DB entries: "YYYY-MM-DD HH:MM:SS"
        if isinstance(doc["timestamp"], pd.Timestamp):
            doc["timestamp"] = doc["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

        collection.update_one(
            {"timestamp": doc["timestamp"]},
            {"$set": doc},
            upsert=True
        )

    print(f"Inserted {len(docs)} documents into MongoDB Atlas")
    return True