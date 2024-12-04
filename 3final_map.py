import pandas as pd
from folium import Map, Marker, Circle, DivIcon
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from geopy.distance import geodesic
import webbrowser
import math

# Load the CSV file
data_path = 'transformed_zip_code_data.csv'
zip_data = pd.read_csv(data_path)

# Handle missing or anomalous data in 'income' column
zip_data['income'] = pd.to_numeric(zip_data['income'], errors='coerce')
zip_data.dropna(subset=['income'], inplace=True)

# Convert income and population to integers
zip_data['income'] = zip_data['income'].astype(int)
zip_data['population'] = zip_data['population'].astype(int)

# Rank incomes and normalize to a 1 to 10 scale
zip_data['income_rank'] = zip_data['income'].rank(method='min')
zip_data['score'] = ((zip_data['income_rank'] - zip_data['income_rank'].min()) / 
                     (zip_data['income_rank'].max() - zip_data['income_rank'].min()) * 9) + 1

# Find the centermost point
center_point = zip_data[['latitude', 'longitude']].mean()

# Create a base map with grayscale tiles
folium_map = Map(location=center_point, zoom_start=10, tiles='cartodbpositron')

# Function to determine circle color based on normalized score
def score_to_color(score):
    return plt.cm.RdYlBu_r(score / 10)  # Using matplotlib colormap reversed Red-Yellow-Blue

# Updated function to calculate minimum distance to the nearest marker
def calculate_min_distance(location, other_locations):
    distances = [geodesic(location, loc).miles for loc in other_locations]
    min_distance = min(distances)
    return min_distance * 1609.34  # Convert miles to meters for folium

# Add markers and circles to the map
for _, row in zip_data.iterrows():
    popup_text = f"<strong>Zip Code:</strong> {int(row['zipcode'])}<br><strong>Income:</strong> ${int(row['income']):,}<br><strong>Population:</strong> {int(row['population']):,}"
    Marker(location=[row['latitude'], row['longitude']], popup=popup_text).add_to(folium_map)
    
    # Calculate minimum distance to the nearest marker
    other_locations = zip_data.loc[zip_data['zipcode'] != row['zipcode'], ['latitude', 'longitude']].values
    min_distance = calculate_min_distance([row['latitude'], row['longitude']], other_locations)
    
    # Convert the RGBA color from score_to_color to a hex color
    circle_color = mcolors.to_hex(score_to_color(row['score']))
    
    Circle(
        location=[row['latitude'], row['longitude']],
        radius=min(min_distance, row['population'] * 10),  # Use min_distance or scaled population as max radius
        color=circle_color,
        fill=True,
        fill_color=circle_color,
        fill_opacity=0.8  # Set the fill opacity to 0.8
    ).add_to(folium_map)
    

def get_circle_point(center, radius, angle):
    """Calculate the latitude and longitude of a point on the circle's circumference."""
    lat, lon = center
    # Convert radius from miles to degrees (approximation)
    radius_in_degrees = radius / 69.0
    new_lat = lat + math.sin(math.radians(angle)) * radius_in_degrees
    new_lon = lon + math.cos(math.radians(angle)) * radius_in_degrees
    return new_lat, new_lon

for radius in [1, 5, 10, 20]:
    circle = Circle(
        location=center_point,
        radius=1609.34 * radius,  # Convert miles to meters
        color='black',
        fill=False
    ).add_to(folium_map)
    
    # Position for the label (e.g., at 45 degrees on the circle's circumference)
    label_position = get_circle_point(center_point, radius, 45)
    
    Marker(
        label_position,
        icon=DivIcon(html=f'<div style="background-color:white; width:40px; height:40px; display:flex; justify-content:center; align-items:center; padding: 2px;">{radius} mile radius</div>')
    ).add_to(folium_map)

# Save the map to an HTML file
folium_map.save('final_map.html')

# Open the map in a web browser
webbrowser.open('final_map.html', new=2)
