import pandas as pd
import json

# Function to convert CSV to JSON records
def csv_to_json(csv_file_path, json_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Create a ticket and paste examples from each collection
    # Pinpoint where each header comes from
    # Rename headers (map col names)
    df = df.rename(columns={})

    # Convert DataFrame to JSON format
    json_records = df.to_dict(orient='records')

    # Write JSON records to a file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_records, json_file, indent=4)
    
    print(f"JSON records saved to {json_file_path}")

# Specify the path to your CSV file and the output JSON file
csv_file_path = '../csv_exports/biomuta.stats.csv'  # Adjust this path
json_file_path = '../json_exports/biomuta.stats.json'  # Adjust this path

# Convert the CSV to JSON
csv_to_json(csv_file_path, json_file_path)
