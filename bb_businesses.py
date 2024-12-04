from apify_client import ApifyClient
import geopandas as gpd
import pandas as pd
from shapely import wkt
import json
import csv
import subprocess

csv_file_path = 'test_area.csv'

# Load the CSV file into a Pandas DataFrame
df = pd.read_csv(csv_file_path)

# Convert the 'geometry' column from WKT to Shapely geometry objects
df['geometry'] = df['geometry'].apply(wkt.loads)

# Convert the DataFrame to a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Initialize the ApifyClient with your API token
client = ApifyClient("apify_api_qnEi70qzc2keJvtKfwjqrAv754dGdm2g50Q1")

# Function to convert GeoDataFrame row to GeoJSON Feature
def row_to_geojson_feature(row):
    return {
        "type": "Feature",
        "geometry": gpd.GeoSeries([row['geometry']]).__geo_interface__["features"][0]["geometry"],
        "properties": {
            "index": row.name
        }
    }

# Function to parse JSON to CSV
def parse_json_to_csv(json_file, csv_file):
    # Open and load the JSON file
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Open the CSV file for writing
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(['Latitude', 'Longitude', 'Day', 'Hour', 'OccupancyPercent'])

        # Iterate through each entry in the JSON data
        for entry in data:
            lat = entry.get('location', {}).get('lat', '')
            lng = entry.get('location', {}).get('lng', '')
            popular_times = entry.get('popularTimesHistogram', {})
            
            # Iterate through each day in the popularTimesHistogram
            for day, hours in popular_times.items():
                # Iterate through each hour's data
                for hour_data in hours:
                    hour = hour_data.get('hour', '')
                    occupancy = hour_data.get('occupancyPercent', '')
                    # Write a row for each hour's data
                    writer.writerow([lat, lng, day, hour, occupancy])

# Select the first row of the GeoDataFrame
row = gdf.iloc[0]

# Convert the selected row to GeoJSON Feature
feature = row_to_geojson_feature(row)
customGeolocation = {
    "type": "FeatureCollection",
    "features": [feature]
}

# Prepare the Actor input with the dynamically generated customGeolocation for the selected feature
run_input = {
    "customGeolocation": customGeolocation,
    # Other parameters remain unchanged
    "deeperCityScrape": True,
    "includeWebResults": False,
    "language": "en",
    "maxCrawledPlacesPerSearch": 20,
    "maxImages": 0,
    "maxReviews": 0,
    "onlyDataFromSearchPage": False,
    "scrapeDirectories": False,
    "scrapeResponseFromOwnerText": True,
    "scrapeReviewId": True,
    "scrapeReviewUrl": True,
    "scrapeReviewerId": True,
    "scrapeReviewerName": True,
    "scrapeReviewerUrl": True,
    "searchStringsArray": [
        "apartments",
        "airport",
        "bus_station",
        "car_rental",
        "housing",
        "lodging",
        "subway_station",
        "taxi_stand",
        "train_station",
        "transit_station",
        "rv_park",
        "campground",
        "light_rail_station",
        "parking",
        "neighborhood",
        "town_square",
        "accounting",
        "airport",
        "aquarium",
        "art gallery",
        "atm",
        "bakery",
        "bank",
        "bar",
        "beauty salon",
        "bicycle store",
        "book store",
        "bowling alley",
        "bus station",
        "cafe",
        "car dealer",
        "car rental",
        "car repair",
        "car wash",
        "casino",
        "cemetery",
        "church",
        "clothing store",
        "convenience store",
        "courthouse",
        "dentist",
        "department store",
        "doctor",
        "drugstore",
        "electrician",
        "electronics store",
        "fire station",
        "florist",
        "funeral home",
        "furniture store",
        "gas station",
        "gym",
        "hair care",
        "hardware store",
        "hindu temple",
        "home goods store",
        "hospital",
        "insurance agency",
        "jewelry store",
        "laundry",
        "lawyer",
        "library",
        "light rail station",
        "liquor store",
        "locksmith",
        "lodging",
        "meal delivery",
        "movie rental",
        "movie theater",
        "moving company",
        "museum",
        "night club",
        "painter",
        "park",
        "parking",
        "pet store",
        "pharmacy",
        "physiotherapist",
        "plumber",
        "police",
        "post office",
        "primary school",
        "real estate agency",
        "restaurant",
        "school",
        "secondary school",
        "shoe store",
        "shopping mall",
        "spa",
        "stadium",
        "storage",
        "store",
        "subway station",
        "supermarket",
        "taxi stand",
        "tourist attraction",
        "train station",
        "transit station",
        "university",
        "veterinary care",
        "zoo"
    ],
    "skipClosedPlaces": False
}

# Run the Actor and wait for it to finish for the selected feature
run = client.actor("nwua9Gu5YrADL7ZDj").call(run_input=run_input)

# Fetch Actor results from the run's dataset
items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

# Define the JSON file path for the selected location
json_file_path = f'loc_traffic_1.json'  # Fixed naming for one location

# Write the results to a JSON file
with open(json_file_path, 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=4)

# Print the message
print(f"Results for location 1 have been saved to {json_file_path}.")

# Parse JSON to CSV
csv_file_path = f'all_biz.csv'  # Fixed naming for one location
parse_json_to_csv(json_file_path, csv_file_path)
print(f"CSV file for location 1 has been saved to {csv_file_path}.")
