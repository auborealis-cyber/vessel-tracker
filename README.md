### Analyzing Vessel Movement with Python: A Modular Approach to Predicting, Validating, & Visualizing Positions

This Python script demonstrates an elegant and efficient approach to tracking, predicting, and validating vessel movements based on their current positions, speed, and course. Here's a breakdown of the script, its functionality, and its modular design.
<p align="center">
  <img src="static/logo.png" alt="Cybersecurity" width="100%">
</p>



---




# **Vessel Tracking and Prediction System**

This project is a modular and robust system for tracking, predicting, and validating vessel movements. It uses Python to analyze vessel positions, predict future locations, and validate actual movements against predictions. This system supports data collection, visualization, and position validation using advanced geospatial calculations.

---

## **Table of Contents**

1. [Project Overview](#project-overview)
2. [Core Components](#core-components)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Workflow](#workflow)
6. [File Structure](#file-structure)
7. [Example Output](#example-output)
8. [Key Advantages](#key-advantages)

---

## **Project Overview**

This project tracks vessel movement, predicts future positions, and validates them against actual positions. It uses two key scripts:

1. **`main.py`** - Handles core functions like data collection, position prediction, radius validation, and ship visualization.
2. **`vessel_data_script.py`** - Manages periodic data collection, prediction, and validation, executing the functions defined in `main.py`.

The system pulls live vessel data from an API, predicts where vessels will be, and then checks if the actual position aligns with the prediction. The results are displayed in a Folium-based interactive map with colored ship markers and polyline paths.

---

## **Core Components**

### **1. Configuration Management**
The project uses a YAML file (`config.yaml`) to store essential configuration variables, ensuring flexibility and reducing hardcoded values. Key configuration variables include:

- **API Path**: Endpoint for retrieving vessel data.
- **Default Location**: Default latitude and longitude used as the map's center.
- **Radius**: The distance to search for vessels.
- **Prediction Time**: The time interval used to predict vessel positions.
- **Time Intervals**: How often data is collected, total duration of data collection, and radius used to validate predicted positions.

Example **`config.yaml`** file:
```yaml
api_path: 'https://example.com/api/vessel'
default_location:
  latitude: 37.7749
  longitude: -122.4194
radius: 10
prediction_time_minutes: 10
interval_minutes: 2
total_duration_minutes: 6
radius_km: 10
```

---

### **2. Core Functions (main.py)**

#### **Data Collection**
The `get_vessel_data()` function fetches vessel data from the API and returns a Pandas DataFrame containing the following vessel details:
- **MMSI**: Unique vessel identifier.
- **Name**: Vessel name.
- **Latitude / Longitude**: Current coordinates.
- **Course Over Ground (COG)**: Direction the ship is moving.
- **Speed Over Ground (SOG)**: Speed at which the vessel is moving.
- **Vessel Type**: Type of vessel.

#### **Position Prediction**
The `predict_future_positions()` function predicts vessel locations based on course, speed, and a time interval. It assumes straight-line movement and constant speed.

#### **Validation of Movement**
The `check_within_radius()` function uses the haversine formula to calculate the distance between the predicted and actual positions. It then determines if the vessel’s actual position falls within the expected radius.

#### **Data Visualization**
The `visualize_ships()` function generates an interactive map using Folium. It plots the following elements:
- **Orange Icons**: Ships that did not stay within the predicted radius.
- **Green Icons**: Ships that remained within the predicted radius.
- **Polylines**: Lines showing the path from the ship's original position to its predicted position.

---

### **3. Periodic Data Collection (vessel_data_script.py)**
This script collects and processes vessel data at fixed intervals. It calls functions from `main.py` to handle predictions, validation, and visualization.

**Key Steps in Data Collection:**
1. **Initial Data Collection**: Collects vessel data at the start.
2. **Prediction**: Predicts where each vessel will be after a set period.
3. **Timer and Wait**: Waits for a specified time before collecting new data.
4. **Validation**: Compares the new positions to the predictions.
5. **Visualization**: Displays the results on an interactive map.

---

## **Installation**

1. **Clone the repository**
```bash
git clone https://github.com/auborealis/ais-api.git
cd ais-api
```

2. **Install required packages**
```bash
pip install -r requirements.txt
```

3. **Add the config file**
Ensure that you have a `config.yaml` file and that it is in the root directory
---

## **Usage**

To run the system, execute the following command:
```bash
python vessel_data_script.py
```
The script will periodically collect vessel data, make predictions, and visualize the results. Once completed, it will save an interactive HTML map as **`ships_visualization.html`**.

---

## **Workflow**

1. **Data Collection**: Collect vessel data from the API.
2. **Prediction**: Predict vessel positions.
3. **Wait**: Use a countdown before collecting new data.
4. **Validation**: Check if actual vessel positions are within the expected range.
5. **Visualization**: Plot ships and their paths on a map.

---

## **File Structure**
```
project-folder/
├── main.py                     # Core functions for vessel tracking and prediction
├── vessel_data_script.py       # Executes the tracking process periodically
├── visualize_ships.py          # Visualizes ships based on the most recent data collected
├── config.yaml                 # Configuration file with API, radius, and other key parameters
├── data/                       # Directory for saved CSV files (optional)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── ships_visualization.html    # HTML map visualization of ship positions
```

---

## **Example Output**

Once the process is complete, you'll get an interactive map called **`ships_visualization.html`**. It contains the following elements:
- **Green Markers**: Ships that stayed within the predicted radius.
- **Orange Markers**: Ships that moved outside the predicted radius.
- **Polylines**: Paths from ship positions to predicted positions.

**WITHIN_RADIUS** represents whether the actual position of the ship matches the predicted position

**Sample DataFrame**
```
        MMSI            NAME  LATITUDE  LONGITUDE  ...  NEW_LATITUDE  NEW_LONGITUDE  WITHIN_RADIUS
0  367748490       PHYLLIS T  37.79487 -122.31128  ...      37.79487     -122.31128           True
1  367098550  HEIDI L.BRUSCO  37.85418 -122.38475  ...      37.85418     -122.38475           True

```

---

## **Key Advantages

1. **Modular Design**: Reusable, well-defined functions.
2. **Interactive Maps**: Visualize ship positions, predictions, and routes.
3. **Automation**: Automates data collection and visualization.
4. **Error Handling**: Provides status messages and identifies missing data.

---

## **Conclusion**
This Vessel Tracking and Prediction System offers a detailed way to track ship movements, predict their future positions, and visualize key results. By leveraging csv looping, geospatial analysis, and interactive visualizations, it simplifies maritime tracking processes. Future improvements may include multi-threaded data collection, additional visualization features, or integration with machine learning models for more advanced predictions. For feedback or support, contact aurorat4794@gmail.com