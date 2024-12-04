import os
import pandas as pd
import folium
from shapely import wkt
import osmnx as ox
import subprocess

def add_osm_roads(map, map_center, network_type='drive', csv_file_path='6osm_roads.csv'):
    # Set the distance to 2000 meters
    dist = 16000

    # Check if the CSV file already exists
    if not os.path.exists(csv_file_path):
        print("Downloading road network data within 8000m from the specified center...")
        try:
            # Download the road network within 2000 meters around the map_center
            G = ox.graph_from_point(map_center, dist=dist, network_type=network_type, simplify=True)

            # Convert the road network to GeoDataFrame
            gdf_edges = ox.graph_to_gdfs(G, nodes=False, edges=True, fill_edge_geometry=True)

            # Save the roads data to a CSV file, including geometry in WKT format
            gdf_edges['geometry'] = gdf_edges['geometry'].apply(lambda x: x.wkt)
            gdf_edges.to_csv(csv_file_path, index=False)
            print(f"Road network data saved to {csv_file_path}.")
        except Exception as e:
            print(f"An error occurred while downloading or saving road network data: {e}")
            return  # Exit the function if there was an error
    else:
        print(f"{csv_file_path} already exists. Loading data from the file.")
        # Load the CSV file, and convert 'geometry' from WKT back to Shapely objects
        gdf_edges = pd.read_csv(csv_file_path)
        gdf_edges['geometry'] = gdf_edges['geometry'].apply(wkt.loads)

    # Define road types and their styles
    road_styles = {
        'motorway': {'color': 'red', 'weight': 4},
        'trunk': {'color': 'orange', 'weight': 4},
        'primary': {'color': 'yellow', 'weight': 3},
        'secondary': {'color': 'green', 'weight': 3},
        'tertiary': {'color': 'blue', 'weight': 2},
        'residential': {'color': 'grey', 'weight': 2},
        'unclassified': {'color': 'black', 'weight': 1},
        'service': {'color': 'black', 'weight': 1},
    }

    # Iterate over all road segments
    for idx, row in gdf_edges.iterrows():
        highway_type = row['highway']
        geom = wkt.loads(row['geometry']) if isinstance(row['geometry'], str) else row['geometry']

        # Handle single and multiple highway types
        if isinstance(highway_type, str) and highway_type in road_styles:
            style = road_styles[highway_type]
            # Add PolyLine to the map using geometry coordinates
            folium.PolyLine(locations=[[point[1], point[0]] for point in geom.coords],
                            color=style['color'], weight=style['weight'], opacity=1).add_to(map)

def main():
    # Load user input from the provided CSV file
    user_input_df = pd.read_csv('user_input.csv')

    # Calculate the mean latitude and longitude from the user input to set as the map center
    map_center = [user_input_df['Latitude'].mean(), user_input_df['Longitude'].mean()]

    # Create a map centered at the calculated location
    map = folium.Map(location=map_center, zoom_start=15)

    # Call the function to add OSM roads to the map
    add_osm_roads(map, map_center)

    #next_script = r"C:\Users\Ryan Register\Desktop\BRIXY-v2\0APIs\7_area_scoring.py"

    # Execute the next script
    #subprocess.run(["python", next_script], check=True)
# Check if the script is run directly (and not imported)
if __name__ == "__main__":
    main()
