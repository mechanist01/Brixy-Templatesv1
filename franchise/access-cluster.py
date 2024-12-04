import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
import ast  # For converting string representation of dictionary to dictionary
from geopy.distance import geodesic

def preprocess_dataframe(df):
    df['location'] = df['location'].apply(ast.literal_eval)
    df['latitude'] = df['location'].apply(lambda x: x['latitude'])
    df['longitude'] = df['location'].apply(lambda x: x['longitude'])
    return df

def filter_points_within_radius(df, center_lat, center_lon, radius_km=16.09):  # 10 miles in kilometers
    def is_within_radius(row):
        center = (center_lat, center_lon)
        point = (row['latitude'], row['longitude'])
        return geodesic(center, point).kilometers <= radius_km

    return df[df.apply(is_within_radius, axis=1)]

def analyze_clusters(df, n_clusters=65):
    n_clusters = min(n_clusters, len(df))
    coords = df[['latitude', 'longitude']]
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(coords)
    df['cluster'] = kmeans.labels_

    results = []
    for cluster_label in range(n_clusters):
        cluster_data = df[df['cluster'] == cluster_label]

        if not cluster_data.empty:
            north = cluster_data.loc[cluster_data['latitude'].idxmax()]
            south = cluster_data.loc[cluster_data['latitude'].idxmin()]
            east = cluster_data.loc[cluster_data['longitude'].idxmax()]
            west = cluster_data.loc[cluster_data['longitude'].idxmin()]

            results.append({
                'cluster': cluster_label,
                'centroid_latitude': np.mean(cluster_data['latitude']), 'centroid_longitude': np.mean(cluster_data['longitude']),
                'north_latitude': north['latitude'], 'north_longitude': north['longitude'],
                'south_latitude': south['latitude'], 'south_longitude': south['longitude'],
                'east_latitude': east['latitude'], 'east_longitude': east['longitude'],
                'west_latitude': west['latitude'], 'west_longitude': west['longitude']
            })

    return results

def save_results_to_csv(results, file_name):
    results_df = pd.DataFrame(results)
    results_df.to_csv(file_name, index=False)

# Center point coordinates
center_lat, center_lon = 25.7617, -80.1918

# Load and preprocess CSV file
csv_file = 'all_results_in_radius.csv'  # Replace with your CSV file path
df = pd.read_csv(csv_file)
df = preprocess_dataframe(df)

# Filter points within 10 miles from the center point
df_filtered = filter_points_within_radius(df, center_lat, center_lon)

# Analyze clusters for the filtered DataFrame
clusters = analyze_clusters(df_filtered)

# Save results to CSV file
save_results_to_csv(clusters, 'accessibility_clusters.csv')
