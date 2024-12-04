import pandas as pd
import ast  # For converting string representation of dictionaries into actual dictionaries

# Load the CSV file into a DataFrame
df = pd.read_csv('dd_in_5_mile_radius.csv')

# Function to convert location strings to dictionaries
def string_to_dict(location_str):
    try:
        return ast.literal_eval(location_str)
    except ValueError:
        return {'latitude': None, 'longitude': None}

# Convert the 'location' column to actual dictionaries
df['location'] = df['location'].apply(string_to_dict)

# Extract latitude and longitude into separate columns for easier duplicate checking
df['latitude'] = df['location'].apply(lambda x: x.get('latitude'))
df['longitude'] = df['location'].apply(lambda x: x.get('longitude'))

# Drop duplicates based on latitude and longitude
cleaned_df = df.drop_duplicates(subset=['latitude', 'longitude'])

# Optionally, save the cleaned DataFrame back to a CSV file
cleaned_df.to_csv('ddcleaned_file.csv', index=False)
