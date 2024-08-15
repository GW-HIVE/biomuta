from pymongo import MongoClient
import json
import os

# MongoDB connection details
mongo_client = MongoClient('mongodb://127.0.0.1:8084/')  # Adjust the connection string if needed
db = mongo_client['biomuta_db']  # Replace with your MongoDB database name

# Function to load JSON records from a file and insert them into MongoDB
def insert_json_to_mongo(json_file_path, collection_name):
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        json_records = json.load(json_file)
    
    collection = db[collection_name]
    collection.insert_many(json_records)
    print(f"Inserted {len(json_records)} records into the {collection_name} collection")

# Directory containing JSON files
json_dir = '../json_exports'

# Iterate over all files in the directory
for json_file_name in os.listdir(json_dir):
    if json_file_name.endswith('.json'):
        # Create the full path to the JSON file
        json_file_path = os.path.join(json_dir, json_file_name)
        
        # Use the file name (minus the .json extension) as the collection name
        collection_name = json_file_name.replace('.json', '')
        
        # Insert the JSON records into MongoDB
        insert_json_to_mongo(json_file_path, f"C_{collection_name}")

# Close the MongoDB connection
mongo_client.close()
