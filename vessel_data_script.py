# Standard Library Imports
import time
import os

# Third-Party Library Imports
import yaml
from tqdm import tqdm
import pandas as pd

# Custom Module Imports
from main import get_vessel_data, predict_future_positions, check_within_radius, save_to_csv, visualize_ships

# Get script directory and path to config.yaml
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.yaml")
completion_flag_path = os.path.join(script_dir, "data_collection_complete.txt")

# Load config.yaml
try:
    with open(config_path, "r", encoding="utf-8") as yaml_file:
        config = yaml.safe_load(yaml_file)
except FileNotFoundError as e:
    print(f"❌ Config file not found at {config_path}")
    raise e
except yaml.YAMLError as e:
    print(f"❌ Error parsing YAML file: {e}")
    raise e

# Extract config values
# Numbers here are used when the file cannot get values from config.yaml
default_location = config.get("default_location", {'latitude': 0, 'longitude': 0})
search_radius = config.get("radius", 10)
interval_minutes = config.get("interval_minutes", 2)
total_duration_minutes = config.get("total_duration_minutes", 6)
radius_km = config.get("radius_km", 10)
prediction_time_minutes = config.get("prediction_time_minutes", 10)
# Extract paths for CSV and HTML output
csv_path = config.get("output_paths", {}).get("csv_path", "data/vessel_data.csv")
html_path = config.get("output_paths", {}).get("html_path", "visualizations/ships_visualization.html")

# Function to retrieve vessel data periodically
def retrieve_vessel_data_periodically(latitude, longitude, radius, interval_minutes, total_duration_minutes):
    total_iterations = total_duration_minutes // interval_minutes
    combined_vessel_data = []  # Store all collected vessel data for final visualization

    for i in range(total_iterations):
        print(f"🔄 Starting API request ({i+1}/{total_iterations})")
        # Get vessel data
        vessel_data = get_vessel_data(latitude, longitude, radius)
        if not vessel_data.empty:
            # Predict future positions and include vessel data
            vessel_data = predict_future_positions(vessel_data, prediction_time_minutes)
            # Collect additional position data
            new_vessel_data = get_vessel_data(latitude, longitude, radius)
            if not new_vessel_data.empty:
                vessel_data['NEW_LATITUDE'] = new_vessel_data['LATITUDE']
                vessel_data['NEW_LONGITUDE'] = new_vessel_data['LONGITUDE']
                vessel_data = check_within_radius(vessel_data, radius_km)
            # Display data for debugging
            print(f"📊 Vessel Data for Request {i+1}/{total_iterations}")
            print(vessel_data.head())  # Shows first 5 rows of the DataFrame
            
            # **Debugging Step**: Print the columns of vessel_data
            print("🔍 Debug: ", vessel_data)
            
            if 'WITHIN_RADIUS' in vessel_data.columns:
                print("✅ 'WITHIN_RADIUS' column found in the DataFrame.")
            else:
                print("❌ 'WITHIN_RADIUS' column not found in the DataFrame.")

            # Save to CSV after each loop
            save_to_csv(vessel_data)
            combined_vessel_data.append(vessel_data)  # Store vessel data for final visualization
            print(f"✅ Data for request ({i+1}/{total_iterations}) saved.")
        else:
            print(f"❌ No vessel data for request ({i+1}/{total_iterations}).")
        # Wait for next iteration unless it's the last one
        if i < total_iterations - 1:
            for _ in tqdm(range(interval_minutes * 60), desc="Waiting", unit="sec"):
                time.sleep(1)
    # Final completion message
    print("✅ Data collection complete for all iterations.")
    # Combine all collected data and visualize it
    if combined_vessel_data:
        final_vessel_data = pd.concat(combined_vessel_data, ignore_index=True)
        visualize_ships(final_vessel_data, default_location)
    else:
        print("❌ No vessel data collected for visualization.")


if __name__ == "__main__":
    # Using values from the config.yaml file
    retrieve_vessel_data_periodically(
        latitude=default_location['latitude'],
        longitude=default_location['longitude'],
        radius=search_radius,
        interval_minutes=interval_minutes,
        total_duration_minutes=total_duration_minutes
    )