import math
import pandas as pd
import subprocess  # Make sure to import subprocess

def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Earth's radius in miles
    earth_radius_miles = 3959.0
    distance = earth_radius_miles * c
    return distance

def calculate_boundary_coordinates(lat, lon, distance_miles):
    return {
        'North': lat + (distance_miles / 69),
        'South': lat - (distance_miles / 69),
        'East': lon + (distance_miles / (math.cos(math.radians(lat)) * 69)),
        'West': lon - (distance_miles / (math.cos(math.radians(lat)) * 69))
    }

def find_zipcodes_within_boundary(file_path, original_lat, original_lon, distance_miles):
    # Load CSV file with zip code column treated as string to preserve leading zeros
    df = pd.read_csv(file_path, dtype={'ZIP': str})  # Assuming the zip code column is named 'ZIP'

    # Calculate boundary coordinates for the specified distance
    boundary = calculate_boundary_coordinates(original_lat, original_lon, distance_miles)

    # Filter zip codes within the boundary box
    within_boundary = df[(df['LAT'] <= boundary['North']) & 
                         (df['LAT'] >= boundary['South']) &
                         (df['LNG'] <= boundary['East']) & 
                         (df['LNG'] >= boundary['West'])]

    # Calculate coordinates for the polygon
    polygon_coordinates = [(boundary['North'], boundary['East']),
                           (boundary['South'], boundary['East']),
                           (boundary['South'], boundary['West']),
                           (boundary['North'], boundary['West'])]

    # Check if each zip code is within the specified mile radius
    within_radius = within_boundary[within_boundary.apply(lambda row: haversine(original_lat, original_lon, row['LAT'], row['LNG']) <= distance_miles, axis=1)]

    # Add the polygon coordinates to the DataFrame
    within_radius['Polygon'] = [polygon_coordinates] * len(within_radius)

    # Save the matching zip codes to a CSV file, ensuring zip codes are treated as strings
    within_radius.to_csv('matching_zipcodes.csv', index=False, columns=['ZIP', 'LAT', 'LNG', 'Polygon'])

    # Execute the next script after saving the CSV
    #next_script = "2zipcodes_data.py"
    #subprocess.run(["python", next_script], check=True)

    return within_radius


# Example usage
# Example usage
file_path = 'zipcode.csv'  # Path to the CSV file
user_input_df = pd.read_csv('user_input.csv')
original_lat = user_input_df['Latitude'].iloc[0]
original_lon = user_input_df['Longitude'].iloc[0] 
find_zipcodes_within_boundary(file_path, original_lat, original_lon, 10)  # Set distance to 10 miles
print("Matching zip codes within 20 miles have been saved, and the next script has been executed.")
