from config import MONGODB_URI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from preprocess_data import *
import pandas as pd
import json
from bson import ObjectId
from datetime import datetime


uri = MONGODB_URI
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["air_quality"]
collection = db['measurements']

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)
    
def get_connection_status():
    try:
        client.admin.command('ping')
        return True
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return False
    

def get_recent_readings(limit=100):
    try:
        # Get recent readings, sorted by timestamp
        # No filtering by date - get all available data
        cursor = collection.find({}).sort('timestamp', -1).limit(limit)
        readings = []
        
        for doc in cursor:
            # Convert MongoDB specific types before returning
            readings.append(json.loads(JSONEncoder().encode(doc)))
        
        # Debug info
        if readings:
            oldest = min(r['timestamp'] for r in readings)
            newest = max(r['timestamp'] for r in readings)
            print(f"Retrieved {len(readings)} readings from {oldest} to {newest}")
        
        # Return in chronological order for charts
        return readings[::-1]  # Reverse to get chronological order
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return []
    
    
def get_last_readings(limit=5):
    collection = db['measurements']
    return list(collection.find().sort([("timestamp", -1)]).limit(limit))

# def get_all_readings():
#     """
#     Get all readings from the database without limit
#     Returns readings in chronological order (oldest first)
#     """
#     try:
#         # Get all readings sorted by timestamp (ascending order)
#         cursor = collection.find({}).sort('timestamp', 1)
#         readings = []
        
#         for doc in cursor:
#             # Round numeric fields to 2 decimal places
#             for field in doc:
#                 if isinstance(doc[field], (int, float)) and field != "_id":
#                     doc[field] = round(doc[field], 2)
            
#             # Convert MongoDB specific types
#             readings.append(json.loads(JSONEncoder().encode(doc)))
        
#         # Debug info
#         if readings:
#             oldest = min(r['timestamp'] for r in readings)
#             newest = max(r['timestamp'] for r in readings)
#             print(f"Retrieved {len(readings)} readings from {oldest} to {newest}")
        
#         return readings
#     except Exception as e:
#         print(f"Error retrieving data: {e}")
#         return []


def get_all_readings():
    """
    Get all readings from the database without limit
    Returns readings in chronological order (oldest first)
    """
    try:
        # Get all readings sorted by timestamp (ascending order)
        cursor = collection.find({}).sort('timestamp', 1)
        readings = []
        
        for doc in cursor:
            # Round numeric fields to 2 decimal places
            for field in doc:
                if isinstance(doc[field], (int, float)) and field != "_id":
                    doc[field] = round(doc[field], 2)
            
            # Convert MongoDB specific types (ObjectId, datetime, etc.)
            readings.append(json.loads(JSONEncoder().encode(doc)))
        
        # Safer debug info - avoid min/max comparison on mixed types
        if readings:
            timestamps = [r['timestamp'] for r in readings if r.get('timestamp') is not None]
            if timestamps:
                try:
                    oldest = min(timestamps)
                    newest = max(timestamps)
                    print(f"Retrieved {len(readings)} readings from {oldest} to {newest}")
                except TypeError as te:
                    print(f"Retrieved {len(readings)} readings (mixed timestamp types - cannot sort for debug)")
                    print(f"Sample timestamps: {timestamps[:3]} ...")
            else:
                print(f"Retrieved {len(readings)} readings (no timestamps found)")
        
        return readings
    
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return []
    


def load_data_to_mongodb():
    df = pd.read_csv('../data/main_readings.csv')
    
    # df = scale_data(df)
    
    data_dict = df.to_dict("records")
    
    try:
        result = collection.insert_many(data_dict)
        print(f"Inserted {len(result.inserted_ids)} documents into air_quality.measurements")
        return True
    except Exception as e:
        print(f"Error inserting data: {e}")
        return False

if __name__ == "__main__":
    # Test connection
    if get_connection_status():
        print("Pinged your deployment. You successfully connected to MongoDB!")
    
    # get_last_reading()
    
    # load_data_to_mongodb()
    
    # Uncomment to clear the collection
    # collection.delete_many({})
    # print(get_last_readings())  
