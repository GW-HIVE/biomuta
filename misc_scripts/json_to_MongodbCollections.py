from pymongo import MongoClient
import json
import os

def load_config(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

config = load_config('../api/config.json')

# Extract MongoDB connection details from the configuration
db_name = config['dbinfo']['dbname']
mongo_port = config['dbinfo']['port']['tst']  # Replace 'tst' with the correct environment if needed
mongo_host = f"mongodb://127.0.0.1:{mongo_port}/"
admin_user = config['dbinfo']['admin']['user']
admin_pass = config['dbinfo']['admin']['password']
admin_db = config['dbinfo']['admin']['db']

# MongoDB connection with authentication
mongo_client = MongoClient(mongo_host, username=admin_user, password=admin_pass, authSource=admin_db)
db = mongo_client[db_name]

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
