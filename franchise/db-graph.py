import sys
import pandas as pd
import plotly.graph_objects as go
import requests

# Load JSON data
json_file_path = 'transformed_zipcodedata.json'  # Adjust this path as necessary

# Check if the JSON file is empty
try:
    df = pd.read_json(json_file_path)
    if df.empty:
        print("JSON data is empty. Terminating script.")
        sys.exit(0)
except ValueError:
    print("Error reading JSON file or file is empty. Terminating script.")
    sys.exit(0)

# Continue with the rest of the script if JSON data is not empty

# Convert 'income' and 'population' to numeric, setting errors='coerce' to handle invalid parsing
df['income'] = pd.to_numeric(df['income'], errors='coerce')
df['population'] = pd.to_numeric(df['population'], errors='coerce')

# Filter out rows where 'income' or 'population' is NaN
df.dropna(subset=['income', 'population'], inplace=True)

# Ensure zip codes are formatted as 5-digit strings
df['zipcode'] = df['zipcode'].apply(lambda x: f"{int(x):05d}")

# Extract zip codes into an array
zipcodes_array = df['zipcode'].tolist()

# Create a figure with a secondary y-axis
fig = go.Figure()

# Add income as a bar chart with the specified color #368EDC
fig.add_trace(go.Bar(x=df['zipcode'], y=df['income'], name='Income', marker_color='#368EDC'))

# Add population as a line chart on the secondary y-axis
fig.add_trace(go.Scatter(x=df['zipcode'], y=df['population'], name='Population', mode='lines+markers', yaxis='y2'))

# Create layout with secondary y-axis for population
fig.update_layout(
    title='Income and Population by Zip Code',
    xaxis_title='Zip Code',
    yaxis_title='Income',
    yaxis2=dict(title='Population', overlaying='y', side='right'),
    legend=dict(x=0.01, y=0.99, bordercolor='LightSteelBlue', bgcolor='LightSteelBlue', borderwidth=1)
)

# Convert the Plotly figure to an HTML div string
html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')

# The URL to which the HTML will be sent
url = 'https://brixv2.bubbleapps.io/api/1.1/wf/report-zipcodes'

# Read user information from user.txt
with open('user.txt', 'r') as file:
    user = file.read().strip()

# Prepare the headers with the API token
headers = {
    'Authorization': 'Bearer b6d8bcec0a876cd19ee0e0c782084c90',
    'Content-Type': 'application/json'
}

# Send a POST request with the HTML content, user data, and zip codes
response = requests.post(url, headers=headers, json={'users': [user], 'html_content': [html_str], 'zipcodes': zipcodes_array})

# Check response
if response.status_code == 200:
    print('HTML content, user info, and zip codes sent successfully!')
else:
    print('Failed to send HTML content, user info, and zip codes. Status code:', response.status_code)
