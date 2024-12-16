# Standard Library Imports
import time
import os
from math import radians, cos, sin, atan2, degrees, sqrt, asin
from visualize_ships import visualize_ships  # Import the visualization module


# Third-Party Library Imports
import requests
import pandas as pd
import yaml  # pip install pyyaml
from tqdm import tqdm


# Ensure full DataFrame display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


# Get script directory and path to config.yaml
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.yaml")


# Load YAML Configuration with Error Handling
try:
    with open(config_path, "r", encoding="utf-8") as yaml_file:
        config = yaml.safe_load(yaml_file)
except FileNotFoundError as exc:
    raise FileNotFoundError(f"❌ Config file not found at {config_path}") from exc
except yaml.YAMLError as exc:
    raise ValueError(f"❌ Error parsing YAML file: {exc}") from exc


# Extract configuration variables
api_path = config.get("api_path")
default_location = config.get("default_location", {'latitude': 0, 'longitude': 0})
search_radius = config.get("radius", 10)
prediction_time_minutes = config.get("prediction_time_minutes", 10)
radius_km = config.get("radius_km", 10)  # Keeping the global scope name for clarity


# Function to fetch vessel data from API
def get_vessel_data(latitude, longitude, radius):
    payload = {'lat': latitude, 'lon': longitude, 'radius': radius}


    try:
        response = requests.post(api_path, data=payload, timeout=10)
        response.raise_for_status()
        response_data = response.json()
        keys_to_include = ['MMSI', 'NAME', 'LATITUDE', 'LONGITUDE', 'COG', 'SOG', 'VESSEL_TYPE']
        return pd.DataFrame(response_data)[keys_to_include]
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed: {e}")
        return pd.DataFrame({"error": [f"❌ API call failed: {e}"]})


# Function to predict vessel positions based on course, speed, and time
def predict_position(latitude, longitude, course, speed, time_minutes):
    latitude, longitude, course = radians(latitude), radians(longitude), radians(course)
    distance_nm = (speed / 60) * time_minutes
    earth_radius_nm = 3440.065  # Earth radius in nautical miles


    predicted_latitude = asin(sin(latitude) * cos(distance_nm / earth_radius_nm) +
                              cos(latitude) * sin(distance_nm / earth_radius_nm) * cos(course))
    predicted_longitude = longitude + atan2(
        sin(course) * sin(distance_nm / earth_radius_nm) * cos(latitude),
        cos(distance_nm / earth_radius_nm) - sin(latitude) * sin(predicted_latitude)
    )
    return degrees(predicted_latitude), degrees(predicted_longitude)


# Function to calculate distance using the haversine formula
def haversine(lat1, lon1, lat2, lon2):
    earth_radius_km = 6371  # Earth's radius in kilometers
    delta_lat, delta_lon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(delta_lat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(delta_lon / 2)**2
    return 2 * earth_radius_km * atan2(sqrt(a), sqrt(1 - a))


# Function to check if a point is within a given radius
def is_point_within_circle(center_lat, center_lon, radius_km, point_lat, point_lon):
    return haversine(center_lat, center_lon, point_lat, point_lon) <= radius_km


# Function to predict future positions for all vessels
def predict_future_positions(df, time_minutes):
    predicted_latitudes = []
    predicted_longitudes = []


    for _, row in df.iterrows():
        lat, lon, cog, sog = row['LATITUDE'], row['LONGITUDE'], row['COG'], row['SOG']
        predicted_lat, predicted_lon = predict_position(lat, lon, cog, sog, time_minutes)
        predicted_latitudes.append(predicted_lat)
        predicted_longitudes.append(predicted_lon)


    df['PREDICTED_LATITUDE'] = predicted_latitudes
    df['PREDICTED_LONGITUDE'] = predicted_longitudes
    return df


# Timer function with progress bar
def start_timer(minutes):
    total_seconds = minutes * 60
    for _ in tqdm(range(total_seconds), desc="⏳ Progress", unit="sec"):
        time.sleep(1)
    print("Timer complete✅")


# Function to check if new positions are within the radius of predicted positions
def check_within_radius(df, radius_km):
    results = []
    for _, row in df.iterrows():
        predicted_lat = row['PREDICTED_LATITUDE']
        predicted_lon = row['PREDICTED_LONGITUDE']
        new_lat = row['NEW_LATITUDE']
        new_lon = row['NEW_LONGITUDE']
        results.append(is_point_within_circle(predicted_lat, predicted_lon, radius_km, new_lat, new_lon))
    df['WITHIN_RADIUS'] = results
    return df


# Main program
print('Accessing API to get vessel data...')
result = get_vessel_data(
    latitude=default_location['latitude'],
    longitude=default_location['longitude'],
    radius=search_radius
)


if result.empty:
    print("❌ No vessel data retrieved. Exiting program.")
else:
    predicted_df = predict_future_positions(result, prediction_time_minutes)
    print(predicted_df.head())


    start_timer(prediction_time_minutes)


    print("Accessing API again to get updated vessel positions...")
    new_result = get_vessel_data(
        latitude=default_location['latitude'],
        longitude=default_location['longitude'],
        radius=search_radius
    )


    if not new_result.empty:
        predicted_df['NEW_LATITUDE'] = new_result['LATITUDE']
        predicted_df['NEW_LONGITUDE'] = new_result['LONGITUDE']


        predicted_df = check_within_radius(predicted_df, radius_km)
        print(predicted_df)
    else:
        print("❌ No new vessel data retrieved.")
       
    if not result.empty:
        predicted_df = predict_future_positions(result, prediction_time_minutes)
        predicted_df = check_within_radius(predicted_df, radius_km)    
        # Visualize the ships
        visualize_ships(predicted_df, default_location)
    else:
        print("❌ No vessel visuals retrieved.")
       
def save_to_csv(vessel_data, file_path="data/vessel_data_log.csv"):
    """Saves vessel data to a CSV file, appending to it if it exists."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Check if the file already exists to determine whether to include headers
    file_exists = os.path.isfile(file_path)
    
    # Append data to the CSV file, including headers only if the file doesn't exist
    vessel_data.to_csv(file_path, mode='a', header=not file_exists, index=False)
    print(f"✅ Vessel data saved to {file_path}")

