# pip install exif
import os
import json
import shutil
from PIL import Image
from exif import Image as ExifImage

def reduce_image_quality(filename, input_folder, output_folder, quality=10):
    if filename.lower().endswith(('.jpg', '.jpeg')):
        img = Image.open(os.path.join(input_folder, filename))
        exif = img.info['exif']
        img.save(os.path.join(output_folder, filename), 'JPEG', exif=exif, quality=quality)
    else:
        print(f'Error image is not a JPEG: {filename}')

def get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return degrees + minutes + seconds

def get_exif_data(image_path):
    with open(image_path, 'rb') as image_file:
        image = ExifImage(image_file)
    return image

def get_lat_lon(image):
    if image.has_exif and 'gps_latitude' in dir(image) and 'gps_longitude' in dir(image):
        lat = get_decimal_from_dms(image.gps_latitude, image.gps_latitude_ref)
        lon = get_decimal_from_dms(image.gps_longitude, image.gps_longitude_ref)
        return lat, lon
    else:
        return None, None

def move_file(src, dst):
    shutil.move(src, dst)

def create_geojson(features, output_file):
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    with open(output_file, 'w') as f:
        json.dump(geojson, f)

def create_geojson_line_by_line(features, output_file):
    with open(output_file, 'w') as f:
        for feature in features:
            geojson = {
                "type": "FeatureCollection",
                "features": [feature]
            }
            f.write("" + json.dumps(geojson) + "\n")

def main(input_folder, output_folder, no_exif_folder, output_file):
    features = []

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(no_exif_folder):
        os.makedirs(no_exif_folder)

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        exif_data = get_exif_data(file_path)
        lat, lon = get_lat_lon(exif_data)
        if lat and lon:
            # reduce image quality
            reduce_image_quality(filename, input_folder, output_folder)

            feature = {
                "type": "Feature",
                "properties": {
                    "externalId": filename,
                    "img_url": f'https://raw.githubusercontent.com/Binnette/mr-challenges/main/HikingSigns/photos/{filename}',
                    "tourism": "information",
                    "information": "guidepost",
                    "hiking": "yes"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            }
            features.append(feature)
            # Reduce image quality
        else:
            move_file(file_path, os.path.join(no_exif_folder, filename))
        
    create_geojson_line_by_line(features, output_file)
    print(f'Done. Challenge file created: {output_file}')

main("src", "photos", "no-exif", "HikingSigns.geojson")
