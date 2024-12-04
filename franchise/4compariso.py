import pandas as pd
import json
from shapely.geometry import Point, Polygon

# Load the McDonald's locations CSV
mcdonalds_df = pd.read_csv('mcdonalds_in_5_mile_radius.csv')

# Load and parse the JSON file containing the polygons
with open('modified_zipcode_polygons.json', 'r') as file:
    polygons_json = json.load(file)

# Initialize an empty list to store the results
results = []

# Iterate through each feature in the JSON
for feature in polygons_json:
    attributes = feature.get('attributes', {})  # Use .get() to avoid KeyError if 'attributes' is missing
    zip_code = attributes.get('ZIP_CODE')
    pop_sqmi = attributes.get('POP_SQMI')
    income = attributes.get('income')
    population = attributes.get('population')
    
    # Proceed only if ZIP_CODE is present
    if zip_code:
        polygon_coords = feature.get('geometry', {}).get('rings', [[]])[0]
        polygon = Polygon(polygon_coords)
        
        # Count how many McDonald's entries fall within this polygon
        location_count = sum(polygon.contains(Point(row['location']['longitude'], row['location']['latitude'])) for _, row in mcdonalds_df.iterrows())
        
        # Append the information to the results list
        results.append({
            'ZIP_CODE': zip_code,
            'POP_SQMI': pop_sqmi,
            'Income': income,
            'Population': population,
            'McDonalds_Count': location_count
        })

# Convert the results list to a DataFrame
results_df = pd.DataFrame(results)

# Save the DataFrame to a new CSV file
results_df.to_csv('results_file.csv', index=False)
