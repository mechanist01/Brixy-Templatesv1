import requests
import pandas as pd
import math

def read_viewport_coordinates(csv_file_path):
    """Read viewport coordinates from a CSV file."""
    df = pd.read_csv(csv_file_path)
    low_lat = df['Min Latitude'].iloc[0]
    low_lon = df['Min Longitude'].iloc[0]
    high_lat = df['Max Latitude'].iloc[0]
    high_lon = df['Max Longitude'].iloc[0]
    return low_lat, low_lon, high_lat, high_lon

def make_text_search_request(api_key, text_query, low_lat, low_lon, high_lat, high_lon, field_mask):
    """Make a text search request with a rectangular viewport location restriction."""
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': field_mask
    }
    data = {
        'textQuery': text_query,
        'locationRestriction': {
            'rectangle': {
                'low': {'latitude': low_lat, 'longitude': low_lon},
                'high': {'latitude': high_lat, 'longitude': high_lon}
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Response JSON:", response.json())  # Print the response JSON
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def search_in_viewport(api_key, text_query, field_mask, csv_file_path):
    """Search within a viewport defined by coordinates from a CSV file."""
    low_lat, low_lon, high_lat, high_lon = read_viewport_coordinates(csv_file_path)
    response = make_text_search_request(api_key, text_query, low_lat, low_lon, high_lat, high_lon, field_mask)
    if response and 'places' in response:
        return response['places']
    return []

def save_to_csv(results, filename):
    """Save search results to a CSV file."""
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)

# Example usage
api_key = "AIzaSyDTF3YQwyT01bi2xm4uf_jdTqt8b2eAc-8"  # Replace with your actual API key
text_query = "Dunkin' Donuts"
field_mask = "places.displayName,places.location"
csv_file_path = 'viewport_coordinates.csv'  # Replace with the actual path to your CSV file

results = search_in_viewport(api_key, text_query, field_mask, csv_file_path)
save_to_csv(results, 'dd_in_viewport.csv')
