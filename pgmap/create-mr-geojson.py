# Import the modules
import json
import os
import re

# Define the input and output folders
input_folder = "extract"
output_folder = "out"

# Create the output folder if it does not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Define the function
def create_feature(id, name, url, type, lon, lat):
    # Create an object with the given parameters
    feature = {
        "type": "Feature",
        "properties": {
            "id": id,
            "name": name,
            "img": url,
            "hd": f'{url}=s1600', # HD image
            "dl": f'{url}=d', # Download link
            "type": type
        },
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        }
    }
    # Return the object
    return feature

def create_geojson_line_by_line(features, output_file):
    with open(output_file, 'w') as f:
        for feature in features:
            geojson = {
                "type": "FeatureCollection",
                "features": [feature]
            }
            f.write("" + json.dumps(geojson) + "\n")

# Initialize a dictionary to store the geojson features for each city
city_features = {}

# Loop through the input files
for file in os.listdir(input_folder):
    # Check if the file is a json file
    if file.endswith(".json"):
        # Get the city name from the file name
        city_name = re.match(r"(\w+)_\d+\.json", file).group(1)
        # Open the file and load the json data
        with open(os.path.join(input_folder, file), "r") as f:
            data = json.load(f)
        # Data are inside a data object in the json file
        if "data" in data:
            data = data["data"]
        # Check if the city name is already in the dictionary
        if city_name not in city_features:
            # If not, create an empty list for that city
            city_features[city_name] = []
        # Check if the data object has a gyms or a pokestops array
        if "gyms" in data or "pokestops" in data:
            # Loop through the gyms array if it exists
            if "gyms" in data:
                for gym in data["gyms"]:
                    # Extract the properties id, name, url, lat, lon from each gym
                    id = gym["id"]
                    name = gym["name"]
                    url = gym["url"]
                    lat = gym["lat"]
                    lon = gym["lon"]
                    # Create a geojson feature of type Point with the properties and coordinates
                    feature = create_feature(id, name, url, "gym", lon, lat)
                    # Append the feature to the list of features for that city
                    city_features[city_name].append(feature)
            # Loop through the pokestops array if it exists
            if "pokestops" in data:
                for pokestop in data["pokestops"]:
                    # Extract the properties id, name, url, lat, lon from each pokestop
                    id = pokestop["id"]
                    name = pokestop["name"]
                    url = pokestop["url"]
                    lat = pokestop["lat"]
                    lon = pokestop["lon"]
                    # Create a geojson feature of type Point with the properties and coordinates
                    feature = create_feature(id, name, url, "pokestop", lon, lat)
                    # Append the feature to the list of features for that city
                    city_features[city_name].append(feature)

# Loop through the dictionary keys (city names)
for city_name in city_features.keys():
    # Create a geojson object with the features list for that city
    features = city_features[city_name]
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    # Determine filename
    filename = city_name + ".geojson"
    filenameLineByLine  = city_name + "_byline.geojson"
    # Save the geojson object as a new file in the output folder with the city name
    with open(os.path.join(output_folder, filename), "w") as f:
        json.dump(geojson, f, indent=4)
    create_geojson_line_by_line(features, os.path.join(output_folder, filenameLineByLine))

    # Write log
    print(f'Dump {len(city_features[city_name])} features in files: {filename} and {filenameLineByLine}')
