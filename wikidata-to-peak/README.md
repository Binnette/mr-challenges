# Add wikidata tag to OSM peaks

- [MapRoulette Challenge](https://maproulette.org/browse/challenges/41844)

## Create the challenge in MapRoulette

### Detailed instructions

Review the proposed edit for the peak "{{name}}":
1. Check the [wikidata article](<http://www.wikidata.org/entity/{{wikidata}}>)
2. Check the [wikipedia article](<https://en.wikipedia.org/wiki/{{wikipedia}}>)
3. Check elevation ({{ele}}) by looking to the elevation lines:
    - [MapCompare](https://mc.bbbike.org/mc/?lon={{#mapLon}}&lat={{#mapLat}}&zoom=18&num=6&mt0=tracestrack-topo&mt1=thunderforest-outdoors&mt2=cyclosm&mt3=geofabrik-topo&mt4=esri-topo&mt5=outdooractive-summer-osm) with [Tracestrack](https://www.openstreetmap.org/#map=18/{{#mapLat}}/{{#mapLon}}&layers=P), Thunderforest Outdoor, [CyclOsm](https://www.cyclosm.org/#map=17/{{#mapLat}}/{{#mapLon}}/cyclosm), Geofabric Topo, Esri Topo and Outdoor active
    - [Refuges.info](http://maps.refuges.info/?zoom=18&lat={{#mapLat}}&lon={{#mapLon}}&layers=B0) - [OpenTopoMap](https://opentopomap.org/#map=16/{{#mapLat}}/{{#mapLon}}) - [CycleMap](https://www.opencyclemap.org/?zoom=18&lat={{#mapLat}}/&lon={{#mapLon}}&layers=B0000) - [Outdoors](https://www.opencyclemap.org/?zoom=18&lat=45.1636&lon=5.98541&layers=B0000)
4. Then press yes to accept the changes (shown on top of the map)

----

All the links below will work only on MapRoulette, because they use {{mustache}} tags that MapRoulette will replace by data: coordinates of the map or tags of the current shown peak.

### Create the challenge.geojson file

1. Run the python script: `get_wikidata.py`
2. Wait around 1 hour...
3. Run the [mr-cli](https://github.com/maproulette/mr-cli) command:

    `mr cooperative tag peaks_with_changes.osm --out challenge.geojson`

Then just import this file when you create or update your challenge in MapRoulette.

#### Details about `get_peaks.py`

1. The script will first query Overpass to get all OSM peaks without wikidata (10mn)
2. Then query wikidata with the names of all the peaks (10mn)
    - Instead of querying wikidata for peaks 1 by 1. I made big queries with a lot of peaks.
    - I had to limit the size of my queries to avoid wikidata returning 500.
    - The script will retry the queries on error 429 (Too many requests).
3. Finally add the wikidata/wikipedia tags to the peaks (40mn)
    - I used multiprocessing for this task, but still it is very long...


Note: the script is based on the name but will check is the distance between the wikidata peak and the OSM peak is lesser than 100 meters

----

The Overpass query used to get peaks with tag wikidata but no tag ele:
```
node[natural=peak][wikidata][!ele];
out meta;
```

Click to run it on [Overpass Turbo](http://overpass-turbo.eu/s/1BZr)