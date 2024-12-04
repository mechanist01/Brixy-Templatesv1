import json
import csv

# Function to process the JSON data and find the global min/max coordinates
def process_json_and_write_csv(json_file_path, csv_file_path):
    with open(json_file_path) as json_file:
        data = json.load(json_file)  # This is now a list, not a dictionary

        # Initialize min/max values with arbitrary large/small numbers
        min_lat = float('inf')
        max_lat = float('-inf')
        min_lon = float('inf')
        max_lon = float('-inf')

        # Loop through each item in the list (each item is a dictionary)
        for item in data:
            # Then loop through each feature's geometry
            for feature in item['features']:
                for polygon in feature['geometry']['rings']:
                    for coord in polygon:
                        lon, lat = coord

                        # Update min/max values if current coordinates are outside the current bounds
                        min_lat = min(min_lat, lat)
                        max_lat = max(max_lat, lat)
                        min_lon = min(min_lon, lon)
                        max_lon = max(max_lon, lon)

        # Write the min/max coordinates to a CSV file
        with open(csv_file_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Min Latitude', 'Max Latitude', 'Min Longitude', 'Max Longitude'])
            csv_writer.writerow([min_lat, max_lat, min_lon, max_lon])

# Path to the input JSON file and the output CSV file
json_file_path = 'modified_zipcode_polygons.json'
csv_file_path = 'viewport_coordinates.csv'

# Call the function with the file paths
process_json_and_write_csv(json_file_path, csv_file_path)
