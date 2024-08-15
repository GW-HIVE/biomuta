from pymongo import MongoClient
import json

# MongoDB connection details
mongo_client = MongoClient('mongodb://localhost:27017/')  # Adjust the connection string if needed
db = mongo_client['biomuta_db']  # Replace with your MongoDB database name

# Function to load JSON records from a file and insert into MongoDB
def insert_json_to_mongo(json_file_path, collection_name):
    # Open and read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        json_records = json.load(json_file)
    
    # Insert JSON records into MongoDB collection
    collection = db[collection_name]
    collection.insert_many(json_records)
    print(f"Inserted {len(json_records)} records into the {collection_name} collection")

# Specify the path to your JSON file and the target MongoDB collection
json_file_path = '../json_exports/biomuta.stats.json'  # Adjust this path if needed
collection_name = 'C_biomuta.stats'  # Collection name in MongoDB

# Insert JSON records into the specified MongoDB collection
insert_json_to_mongo(json_file_path, collection_name)

# Close the MongoDB connection
mongo_client.close()
