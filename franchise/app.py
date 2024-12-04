from flask import Flask, request, jsonify
import pandas as pd
from shapely.geometry import Point, Polygon
import requests
import json
import subprocess

app = Flask(__name__)

def extract_zipcodes_from_polygon(polygon_coords, csv_file_path):
    coords_list = polygon_coords.split(',')
    polygon_points = [(float(coords_list[i]), float(coords_list[i + 1])) for i in range(0, len(coords_list) - 1, 2)]
    
    if polygon_points[0] != polygon_points[-1]:
        polygon_points.append(polygon_points[0])
    
    polygon = Polygon(polygon_points)
    
    df = pd.read_csv(csv_file_path)
    
    zipcodes_within_polygon = []
    
    for index, row in df.iterrows():
        point = Point(row['LNG'], row['LAT'])
        
        if polygon.contains(point):
            zipcodes_within_polygon.append(int(row['ZIP']))  # Convert to int to remove any decimal point
    
    return zipcodes_within_polygon

def fetch_data_for_zip(zip_code):
    base_url = "https://data.census.gov/api/profile/content/highlights?g=860XX00US{}"
    modified_url = base_url.format(zip_code)
    response = requests.get(modified_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def transform_data():
    with open('zipcodedata.json', 'r') as file:
        data = json.load(file)

    transformed_data = []

    for zipcode, details in data.items():
        highlights = details['highlights']
        transformed_entry = {
            'zipcode': zipcode,
            'population': None,
            'income': None
        }

        # Check each highlight and extract population and income
        for highlight in highlights:
            if highlight['label'] == 'Total Population':
                transformed_entry['population'] = highlight['value']
            elif highlight['label'] == 'Median Household Income':
                transformed_entry['income'] = highlight['value']
            
        transformed_data.append(transformed_entry)

    with open('transformed_zipcodedata.json', 'w') as file:
        json.dump(transformed_data, file, indent=4)

@app.route('/process_polygon', methods=['POST'])
def process_polygon():
    data = request.json
    user = data.get('user')  # Extract the user from the incoming JSON data
    
    # Save the user to a text file
    with open('user.txt', 'w') as file:
        file.write(user)

    polygon_coords = data.get('polygon_coords')
    csv_file_path = 'zipcode.csv'  # Replace this with your actual CSV file path
    
    if polygon_coords:
        # Save the polygon coordinates to a CSV file
        coords_list = polygon_coords.split(',')
        polygon_points = [(float(coords_list[i]), float(coords_list[i + 1])) for i in range(0, len(coords_list) - 1, 2)]
        polygon_df = pd.DataFrame(polygon_points, columns=['Latitude', 'Longitude'])
        polygon_df.to_csv('polygon.csv', index=False)

        zipcodes_within_polygon = extract_zipcodes_from_polygon(polygon_coords, csv_file_path)
        results = {}
        for zip_code in zipcodes_within_polygon:
            data = fetch_data_for_zip(zip_code)
            if data:
                results[str(zip_code)] = data  # Ensure zip_code is a string for JSON key
        
        # Save fetched data to JSON file
        with open('zipcodedata.json', 'w') as file:
            json.dump(results, file, indent=4)
        
        # Save fetched data to JSON file
        with open('zipcodedata.json', 'w') as file:
            json.dump(results, file, indent=4)
        
        # Transform the data
        transform_data()

        # Specify the paths to the next scripts
        db_graph_script = "db-graph.py"
        radius_zipcodes_script = "1radius-zipcodes.py"

        # Execute the next scripts
        subprocess.run(["python", db_graph_script], check=True)
        subprocess.run(["python", radius_zipcodes_script], check=True)

        # Load and return the transformed data
        with open('transformed_zipcodedata.json', 'r') as file:
            transformed_data = json.load(file)
        
        return jsonify(transformed_data)
    else:
        return jsonify({"error": "Polygon coordinates not provided"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
