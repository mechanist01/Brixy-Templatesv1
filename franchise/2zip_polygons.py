import csv
import requests
import json

# Function to make the API call for a given zip code
def fetch_zipcode_data(zipcode):
    base_url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_ZIP_Code_Areas_anaylsis/FeatureServer/0/query"
    params = {
        'where': f"ZIP_CODE = '{zipcode}'",
        'outFields': 'ZIP_CODE,POP_SQMI,SQMI,Shape__Area,Shape__Length',
        'outSR': '4326',
        'f': 'json'
    }
    response = requests.get(base_url, params=params)
    return response.json()

# Path to your input CSV file
input_csv_path = 'matching_zipcodes.csv'
# Path to your output JSON file
output_json_path = 'zipcode_polygons.json'

# Initialize an empty list to store the response data
data = []

# Read the CSV file and iterate over the zip codes
with open(input_csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        zipcode = row['ZIP']  # Assuming the zip code column is named 'ZIP'
        zipcode_data = fetch_zipcode_data(zipcode)
        data.append(zipcode_data)

# Save the collected data to a JSON file
with open(output_json_path, 'w') as jsonfile:
    json.dump(data, jsonfile, indent=4)

print(f"Data for all zip codes has been fetched and saved to {output_json_path}.")
