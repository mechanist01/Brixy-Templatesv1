import requests
import pandas as pd
import subprocess
from math import radians, cos

def read_viewport_coordinates(csv_file_path):
    """Read viewport coordinates from a CSV file."""
    df = pd.read_csv(csv_file_path)
    low_lat = df['Min Latitude'].iloc[0]
    low_lon = df['Min Longitude'].iloc[0]
    high_lat = df['Max Latitude'].iloc[0]
    high_lon = df['Max Longitude'].iloc[0]
    return low_lat, low_lon, high_lat, high_lon

def find_nearby_places(api_key, text_query, southwest, northeast, field_mask):
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
    print(f"Response from Google for {text_query}: {response.json()}")
    if response.status_code == 200:
        return response.json()['results']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def main():
    api_key = "Your_API_Key_Here"  # Replace with your actual API key
    field_mask = "places.displayName,places.location"  # Example field mask

    # Load location data
    csv_file_path = "user_input.csv"
    df = pd.read_csv(csv_file_path)
    locations = df[['Latitude', 'Longitude']].values.tolist()

    # Load companion types
    csv_file_path_companions = 'companion_types_MAPS.csv'
    df_companions = pd.read_csv(csv_file_path_companions)
    place_types = df_companions['Type 2'].unique()

    all_places = []

    # Distance to move in each direction to define the bounds (meters)
    delta_distance = 1000  # 1000 meters for both latitude and longitude
    # Convert delta_distance to degrees for latitude and longitude
    delta_latitude = delta_distance / 111000  # Approximate conversion for latitude
    delta_longitude = delta_distance / (111000 * cos(radians(locations[0][0])))  # Approximate conversion for longitude

    # Loop over each location
    for location in locations:
        southwest = [location[0] - delta_latitude, location[1] - delta_longitude]
        northeast = [location[0] + delta_latitude, location[1] + delta_longitude]
        for place_type in place_types:
            print(f"Searching for {place_type} in the area bounded by {southwest} and {northeast}...")
            results = find_nearby_places(api_key, place_type, southwest, northeast, field_mask)
            if results:
                all_places.extend(results)

    # Convert the list of dictionaries to a DataFrame
    places_df = pd.DataFrame(all_places)
    # Drop duplicates based on place_id
    places_df = places_df.drop_duplicates(subset=['place_id'])
    # Save results to CSV
    csv_path = "companion_list_MAPS.csv"
    places_df.to_csv(csv_path, index=False)


if __name__ == '__main__':
    main()
