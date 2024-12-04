import requests
import json
import pandas as pd
import subprocess
import time  # Import the time module

def fetch_data_for_zip(zip_code):
    base_url = "https://data.census.gov/api/profile/content/highlights?g=860XX00US{}"
    modified_url = base_url.format(zip_code)
    try:
        response = requests.get(modified_url)
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
        data = response.json()
        if data:
            return data
        else:
            print(f"No data available for ZIP code {zip_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data for ZIP code {zip_code}: {e}")
        return None
    except json.decoder.JSONDecodeError as e:
        print(f"Failed to decode JSON for ZIP code {zip_code}: {e}")
        return None

def fetch_and_save_data(input_csv, output_json):
    zip_codes_df = pd.read_csv(input_csv, dtype={'ZIP': str})
    all_responses = {}
    for _, row in zip_codes_df.iterrows():
        zip_code = row['ZIP']
        data = fetch_data_for_zip(zip_code)
        if data:
            print(f"Data for ZIP code {zip_code}: {json.dumps(data, indent=4)}")
            all_responses[zip_code] = {'data': data, 'lat': row['LAT'], 'lng': row['LNG']}
        else:
            print(f"No data for ZIP code {zip_code}")
        
        time.sleep(3)  # Wait for 3 seconds before making the next call

    with open(output_json, 'w') as file:
        json.dump(all_responses, file, indent=4)
    print(f"Data saved to '{output_json}'")

def transform_data(input_json, output_csv):
    with open(input_json, 'r') as file:
        data = json.load(file)
    transformed_data = []
    for zipcode, details in data.items():
        highlights = details['data'].get('highlights', [])
        transformed_entry = {
            'zipcode': zipcode,
            'latitude': details['lat'],
            'longitude': details['lng'],
            'population': None,
            'income': None
        }
        for highlight in highlights:
            if highlight['label'] == 'Total Population':
                transformed_entry['population'] = highlight['value']
            elif highlight['label'] == 'Median Household Income':
                transformed_entry['income'] = highlight['value']
        transformed_data.append(transformed_entry)
    transformed_df = pd.DataFrame(transformed_data)
    transformed_df.to_csv(output_csv, index=False)
    print(f"Transformed data saved to '{output_csv}'")

# Example usage
input_csv = 'matching_zipcodes.csv'
output_json = 'zip_code_data.json'
output_csv = 'transformed_zip_code_data.csv'

fetch_and_save_data(input_csv, output_json)
transform_data(output_json, output_csv)
