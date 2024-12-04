import pandas as pd
import numpy as np
import ast
from sklearn.cluster import DBSCAN

def preprocess_dataframe(df):
    df['location'] = df['location'].apply(ast.literal_eval)
    df['latitude'] = df['location'].apply(lambda x: x['latitude'])
    df['longitude'] = df['location'].apply(lambda x: x['longitude'])
    return df

def analyze_clusters(df, eps=0.001, min_samples=5):  # eps is roughly 100m in degrees
    coords = df[['latitude', 'longitude']].values
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    df['cluster'] = dbscan.fit_predict(coords)
    
    # Filter out noise points
    clustered_df = df[df['cluster'] != -1]
    
    return clustered_df

# Load and preprocess CSV file
csv_file = 'merged_data.csv'  # Ensure the correct path to the CSV file
df = pd.read_csv(csv_file)
df = preprocess_dataframe(df)

# Analyze clusters using DBSCAN with eps set for 100m
clustered_df = analyze_clusters(df)

# Save the clustered data to a CSV file, excluding noise points
output_csv_file = 'clustered_data.csv'  # Specify the output CSV file path
clustered_df.to_csv(output_csv_file, index=False)

output_csv_file
