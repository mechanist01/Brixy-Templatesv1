import pandas as pd
import folium
import ast  # For converting string representation of dictionaries into actual dictionaries
from shapely import wkt, Polygon
import json
import branca


# Load the CSV file into a DataFrame
df = pd.read_csv('2cleaned_file.csv')  # Make sure the path is correct
df2 = pd.read_csv('dd_in_viewport.csv')  # Make sure the path is correct
clusters_df = pd.read_csv('accessibility_clusters.csv')  # Make sure the path is correct


# Initialize a map at an average location
average_latitude = df['location'].apply(lambda x: ast.literal_eval(x)['latitude']).mean()
average_longitude = df['location'].apply(lambda x: ast.literal_eval(x)['longitude']).mean()

# Define map_center using the average latitude and longitude
map_center = (average_latitude, average_longitude)

# Initialize the Folium map using map_center
folium_map = folium.Map(location=[map_center[0], map_center[1]], zoom_start=12, tiles='cartodbpositron')

# Load the CSV file containing road geometries
roads_df = pd.read_csv('6osm_roads.csv')  # Update the path to your roads CSV file

with open('modified_zipcode_polygons.json') as f:
    data = json.load(f)

# Initialize the Folium map

# Get min and max values of POP_SQMI for the colormap
pop_sqmi_values = [feature['attributes']['POP_SQMI'] for item in data for feature in item['features']]
min_pop_sqmi = min(pop_sqmi_values)
max_pop_sqmi = max(pop_sqmi_values)

# Create a colormap
colormap = branca.colormap.linear.RdYlBu_11.scale(min_pop_sqmi, max_pop_sqmi)

# Iterate through the features and add them to the map
for item in data:
    if 'features' in item:
        for feature in item['features']:
            geometry = feature.get('geometry', {})
            rings = geometry.get('rings', [])
            
            if len(rings) > 0:
                polygon_points = [[point[1], point[0]] for point in rings[0]]
                pop_sqmi = feature['attributes']['POP_SQMI']

                # Get the color for the polygon based on POP_SQMI
                fill_color = colormap(pop_sqmi)

                # Construct the popup message with the desired attributes
                attributes = feature['attributes']
                popup_content = '<br>'.join(f'{key}: {value}' for key, value in attributes.items())
                popup = folium.Popup(popup_content, max_width=300)

                # Create a Folium polygon with the popup and fill color based on POP_SQMI
                folium.Polygon(
                    locations=polygon_points,
                    color='black',
                    weight=2,
                    fill=True,
                    fill_color=fill_color,
                    fill_opacity=0.7,
                    popup=popup
                ).add_to(folium_map)

# Define road styles (customize this based on your roads CSV content and preferences)
road_styles = {
    'motorway': {'color': 'red', 'weight': 4},
    'trunk': {'color': 'orange', 'weight': 4},
    'primary': {'color': 'yellow', 'weight': 3},
    'secondary': {'color': 'green', 'weight': 3},
    'tertiary': {'color': 'blue', 'weight': 2},
}

# Iterate over the roads DataFrame to add each road segment to the map
for idx, row in roads_df.iterrows():
    geom = wkt.loads(row['geometry'])
    road_type = row['highway']  # Adjust 'road_type' to match the actual column name in your CSV
    
    # Skip road types that are not to be displayed
    if road_type in ['residential', 'unclassified', 'service']:
        continue

    style = road_styles.get(road_type, {'color': 'grey', 'weight': 1})  # Use a default style if the road type is not in road_styles

    # Add the road segment as a PolyLine on the Folium map
    folium.PolyLine(
        locations=[[point[1], point[0]] for point in geom.coords],
        color=style['color'],
        weight=style['weight'],
        opacity=0.5
    ).add_to(folium_map)

# Iterate over the clusters DataFrame to draw polygons for each cluster
for _, row in clusters_df.iterrows():
    # Extract polygon points based on the column labels
    polygon_points = [
        (row['north_latitude'], row['north_longitude']),  # North point
        (row['east_latitude'], row['east_longitude']),  # East point
        (row['south_latitude'], row['south_longitude']),  # South point
        (row['west_latitude'], row['west_longitude']),  # West point
        (row['north_latitude'], row['north_longitude'])  # Close the polygon by repeating the North point
    ]

    # Add polygon to map
    folium.Polygon(
        locations=polygon_points,
        color='blue',
        weight=2,
        fill=True,
        fill_color='cyan',
        fill_opacity=0.4,
        popup=f'Cluster {int(row["cluster"])}'
    ).add_to(folium_map)

# Path to your local image file
image_path = 'star.png'  # Use the relative or absolute path to your image file

# Iterate over DataFrame rows to add markers with an image
for index, row in df.iterrows():
    location_dict = ast.literal_eval(row['location'])
    displayName_dict = ast.literal_eval(row['displayName'])

    latitude = location_dict['latitude']
    longitude = location_dict['longitude']
    displayName = displayName_dict['text']

    icon = folium.CustomIcon(
        icon_image=image_path,
        icon_size=(50, 50)  # Set the size of the image (width, height) in pixels
    )

    folium.Marker(
        [latitude, longitude], 
        popup=displayName, 
        icon=icon  # Use the custom icon
    ).add_to(folium_map)

    
### Iterate over DataFrame rows to add markers
image2_path = 'dd.png'  # Use the relative or absolute path to your image file

# Iterate over DataFrame rows to add markers with an image
for index, row in df2.iterrows():
    location_dict = ast.literal_eval(row['location'])
    displayName_dict = ast.literal_eval(row['displayName'])

    latitude = location_dict['latitude']
    longitude = location_dict['longitude']
    displayName = displayName_dict['text']

    icon = folium.CustomIcon(
        icon_image=image2_path,
        icon_size=(50, 50)  # Set the size of the image (width, height) in pixels
    )

    folium.Marker(
        [latitude, longitude], 
        popup=displayName, 
        icon=icon  # Use the custom icon
    ).add_to(folium_map)
    


# Add the colormap to the map
    

# Save the map to an HTML file
map_file = 'a2ccess-final-map.html'  # Ensure you have the correct path
folium_map.save(map_file)
