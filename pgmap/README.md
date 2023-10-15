# PGMAP

POI and images extracted from http://www.pogomap.fr/

## How to create a challenge

1. Open http://www.pogomap.fr/
2. Choose a city
3. In the options, show only gyms and pokestops
4. Open the dev tool of your browser
5. Open the Network tab
6. Save the JSON files that contains the gyms and the pokestops
7. Example with grenoble city:
    - I save the gyms JSON file as `extract/grenoble_1.json`
    - I save the pokestops JSON file as `extract/grenoble_2.json`
8. Then run the python script `create-mr-geojson.py`

This script merge the files from the extract folder. And create a POI task with the picture took by a POGO player.

There are 2 version of the challenge file (with same data):
- grenoble.geosjon: contains a regular geojson file with all the POI to map
- grenoble_byline.geojson: a line by line version as [advised](https://learn.maproulette.org/documentation/line-by-line-geojson/) by MapRoulette for big dataset.
