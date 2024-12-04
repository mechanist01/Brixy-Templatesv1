import pandas as pd
import os

def merge_csv_files(folder_path, output_file):
    # Initialize an empty DataFrame to hold merged data
    merged_df = pd.DataFrame()

    # List all CSV files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # Loop over the list of files
    for file in csv_files:
        # Construct the full file path
        file_path = os.path.join(folder_path, file)
        
        # Read the CSV file and append it to the merged DataFrame
        current_df = pd.read_csv(file_path)
        merged_df = pd.concat([merged_df, current_df], ignore_index=True)

    # Remove duplicates
    merged_df.drop_duplicates(inplace=True)

    # Save the merged and deduplicated data to a new CSV file
    merged_df.to_csv(output_file, index=False)

    print(f"Merged file saved as {output_file}")

# Example usage
folder_path = r'C:\Users\Ryan Register\Desktop\Brixy-Templatesv1\10mile-locations\test'  # Replace with your folder path
output_file = 'merged_data.csv'  # Name of the output file
merge_csv_files(folder_path, output_file)
