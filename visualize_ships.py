import os
import yaml
import folium
from folium.plugins import Search  # ✅ Import Search correctly

#Ensure the file gets put into the right directory:
script_dir = os.path.dirname(os.path.abspath(__file__))    
config_path = os.path.join(script_dir, "config.yaml")
try:
    with open(config_path, "r", encoding="utf-8") as yaml_file:
        config = yaml.safe_load(yaml_file)
except FileNotFoundError as e:
    print(f"❌ Config file not found at {config_path}")
    raise e
except yaml.YAMLError as e:
    print(f"❌ Error parsing YAML file: {e}")
    raise e

def create_map(center_lat, center_lon, zoom_start=12):
    """Create a Folium map centered at the given latitude and longitude."""
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)
    return m

def add_ship_marker(marker_cluster, lat, lon, name, vessel_type, is_within_radius, predicted_lat, predicted_lon):
    """Add a ship marker and polyline to the map."""
    color = 'green' if is_within_radius else 'orange'
    
    # Popup shows Ship name, Vessel type, and Within Radius status
    popup_content = f""" 
    <strong>🚢Ship:</strong> {name}<br>
    <strong>Type:</strong> {vessel_type}<br>
    <strong>Within Radius:</strong> {'Yes✅' if is_within_radius else 'No❌'}
    """
    
    # Add the ship marker to the map
    marker = folium.Marker(
        location=[lat, lon],
        popup=popup_content,
        icon=folium.Icon(color=color)
    )
    marker.add_to(marker_cluster)
    
    # Add a PolyLine from current position to predicted position
    folium.PolyLine(
        locations=[[lat, lon], [predicted_lat, predicted_lon]],
        color=color,
        weight=1,
        opacity=1
    ).add_to(marker_cluster)
    
    return marker

def visualize_ships(vessel_df, default_location):
    """Visualize ships on a Folium map with green and orange markers only."""
    map_obj = create_map(center_lat=default_location['latitude'], center_lon=default_location['longitude'])
    
    # Store all ship information as GeoJSON-like objects
    features = []
    
    # Create a FeatureGroup for the markers
    marker_cluster = folium.FeatureGroup(name="Ship Markers")

    for _, row in vessel_df.iterrows():
        lat, lon = row['LATITUDE'], row['LONGITUDE']
        name = row['NAME']
        vessel_type = row['VESSEL_TYPE']
        predicted_lat = row['PREDICTED_LATITUDE']
        predicted_lon = row['PREDICTED_LONGITUDE']
        is_within_radius = row['WITHIN_RADIUS']
        
        # Only process ships within the radius or those with the orange color
        if is_within_radius or not is_within_radius:
            # Add markers for green and orange ships only
            color = 'green' if is_within_radius else 'orange'
            
            folium.Marker(
                location=[lat, lon],
                popup=f"""
                <strong>🚢Ship:</strong> {name}<br>
                <strong>Type:</strong> {vessel_type}<br>
                <strong>Within Radius:</strong> {'Yes✅' if is_within_radius else 'No❌'}
                """,
                icon=folium.Icon(color=color)
            ).add_to(marker_cluster)
            
            # Add PolyLine from current position to predicted position
            folium.PolyLine(
                locations=[[lat, lon], [predicted_lat, predicted_lon]],
                color=color,
                weight=1,
                opacity=1
            ).add_to(marker_cluster)

            # Add to GeoJSON feature list for Search functionality
            feature = {
                'type': 'Feature',
                'properties': {
                    'name': name,
                    'vessel_type': vessel_type,
                    'within_radius': 'Yes' if is_within_radius else 'No',
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [lon, lat]
                }
            }
            features.append(feature)

    # Create a FeatureGroup layer from the features
    geojson_layer = folium.GeoJson(
        {'type': 'FeatureCollection', 'features': features},
        name="Ship Data"
    ).add_to(map_obj)

    # Add the Search control to the map to search ships by name
    Search(
        layer=geojson_layer,
        search_label='name',
        placeholder='Search for a ship by name...',
        collapsed=False
    ).add_to(map_obj)
    
    # Add the marker cluster to the map
    marker_cluster.add_to(map_obj)

    # Save the map to an HTML file
    map_obj.save("html_path")
    html_path = config.get("output_paths", {}).get("html_path", "data/ships_visualization.html")
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    print("🗺️ Visualization saved as 'data/ships_visualization.html'")