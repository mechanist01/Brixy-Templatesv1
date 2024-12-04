import pandas as pd
import json

# Load the CSV data
csv_file_path = 'transformed_zip_code_data.csv'
csv_data = pd.read_csv(csv_file_path)
csv_data['zipcode'] = csv_data['zipcode'].astype(str)

# Create a dictionary from the CSV data, mapping ZIP codes to the desired data
csv_data_dict = csv_data.set_index('zipcode').to_dict(orient='index')

# Load the JSON data
json_file_path = 'zipcode_polygons.json'
with open(json_file_path, 'r') as json_file:
    json_data = json.load(json_file)

# Iterate through each feature in the JSON data
for item in json_data:
    if 'features' in item:
        for feature in item['features']:
            # Extract the ZIP code from the feature
            zip_code = feature['attributes']['ZIP_CODE']
            
            # Look up the corresponding data from the CSV dictionary
            if zip_code in csv_data_dict:
                # Append the CSV data to the feature's attributes
                feature['attributes']['income'] = csv_data_dict[zip_code]['income']
                feature['attributes']['population'] = csv_data_dict[zip_code]['population']

# Save the modified JSON structure back to a file
modified_json_file_path = 'modified_zipcode_polygons.json'
with open(modified_json_file_path, 'w') as modified_json_file:
    json.dump(json_data, modified_json_file, indent=2)

print(f'Modified JSON file saved to {modified_json_file_path}')
