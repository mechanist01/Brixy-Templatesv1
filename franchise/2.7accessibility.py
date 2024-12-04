import requests
import pandas as pd
import math

def hexagon_grid(center_lat, center_lon, radius_km, hex_size_km):
    hexagons_per_side = math.ceil(radius_km / (1.5 * hex_size_km))
    lat_step = (1.5 * hex_size_km) / 111  # 111 km per latitude degree
    lon_step = (hex_size_km * math.sqrt(3)) / (111 * math.cos(math.radians(center_lat)))

    hex_centers = []
    for q in range(-hexagons_per_side, hexagons_per_side + 1):
        for r in range(-hexagons_per_side, hexagons_per_side + 1):
            if abs(q + r) <= hexagons_per_side:
                new_lat = center_lat + lat_step * r
                new_lon = center_lon + lon_step * (q + r/2)
                hex_centers.append((new_lat, new_lon))
    return hex_centers

def make_text_search_request(api_key, text_query, lat, lon, field_mask):
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': field_mask
    }
    data = {
        'textQuery': text_query,
        'locationBias': {
            'circle': {
                'center': {'latitude': lat, 'longitude': lon},
                'radius': 500.0  # 500 meters radius
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

def search_in_hex_grid(api_key, text_queries, field_mask, center_lat, center_lon, final_radius_km, hex_size_km):
    hex_centers = hexagon_grid(center_lat, center_lon, final_radius_km, hex_size_km)
    all_results = []  # Initialize a list to hold all results from all queries

    for text_query in text_queries:
        print(f"Searching for {text_query}...")
        for lat, lon in hex_centers:
            response = make_text_search_request(api_key, text_query, lat, lon, field_mask)
            if response and 'places' in response:
                for place in response['places']:
                    place['query'] = text_query  # Optionally add the query to each result for reference
                    all_results.append(place)

    # Save all results into one CSV file after collecting from all queries and hexagons
    save_to_csv(all_results, 'all_results_in_radius.csv')

def save_to_csv(results, filename):
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)

def main():
    api_key = "AIzaSyDTF3YQwyT01bi2xm4uf_jdTqt8b2eAc-8"  # Replace with your actual API key
    field_mask = "places.location"
    center_lat = 25.7617  # Example: Central latitude
    center_lon = -80.1918  # Example: Central longitude
    final_radius_km = 10 * 1.60934  # 10 miles in kilometers
    hex_size_km = 2.0  # Set hex size to 1 km to ensure 1000 meters between centers

    # Load text queries from CSV
    types_df = pd.read_csv('accessibility_types.csv')
    text_queries = types_df['types'].tolist()

    # Perform search for each query
    search_in_hex_grid(api_key, text_queries, field_mask, center_lat, center_lon, final_radius_km, hex_size_km)

if __name__ == "__main__":
    main()


####  SET search radius to 500m, keep hexagonal distance the same 3/15 ####
####  SET search radius to 500m, keep hexagonal distance the same 3/15 ####
####  SET search radius to 500m, keep hexagonal distance the same 3/15 ####
####  SET search radius to 500m, keep hexagonal distance the same 3/15 ####
####  SET search radius to 500m, keep hexagonal distance the same 3/15 ####
####  SET search radius to 500m, keep hexagonal distance the same 3/15 ####
####  SET search radius to 500m, keep hexagonal distance the same 3/15 ####
####  SET search radius to 500m, keep hexagonal distance the same 3/15 ####