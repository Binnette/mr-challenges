# Copy peaks elevation from Wikidata

- [MapRoulette Challenge](https://maproulette.org/browse/challenges/23309)

## Create the challenge in MapRoulette

### Detailed instructions

Review if the elevation (tag ele) is correct:
1. Read the elevation lines on the map
    - [MapCompare](https://mc.bbbike.org/mc/?lon={{#mapLon}}&lat={{#mapLat}}&zoom=18&num=6&mt0=tracestrack-topo&mt1=thunderforest-outdoors&mt2=cyclosm&mt3=geofabrik-topo&mt4=esri-topo&mt5=outdooractive-summer-osm) with [Tracestrack](https://www.openstreetmap.org/#map=18/{{#mapLat}}/{{#mapLon}}&layers=P), Thunderforest Outdoor, [CyclOsm](https://www.cyclosm.org/#map=17/{{#mapLat}}/{{#mapLon}}/cyclosm), Geofabric Topo, Esri Topo and Outdoor active
    - [Refuges.info](http://maps.refuges.info/?zoom=18&lat={{#mapLat}}&lon={{#mapLon}}&layers=B0) - [OpenTopoMap](https://opentopomap.org/#map=16/{{#mapLat}}/{{#mapLon}}) - [CycleMap](https://www.opencyclemap.org/?zoom=18&lat={{#mapLat}}/&lon={{#mapLon}}&layers=B0000) - [Outdoors](https://www.opencyclemap.org/?zoom=18&lat=45.1636&lon=5.98541&layers=B0000)
2. Confirm the location by looking at the [Wikidata article](https://www.wikidata.org/wiki/{{wikidata}}) of this peak
3. If the peak has tags "elevation={{elevation}}" or "elev={{elev}}". Move them to "ele={{ele}}"
4. If needed search on [Google](<https://www.google.com/search?q={{name}}>) - [DuckDuckGo](<https://duckduckgo.com/?va=n&t=h_&q={{name}}>) - [Bing](<https://www.bing.com/search?q={{name}}>) - [Bing AI](<https://www.bing.com/search?showconv=1&sendquery=1&q=Give me the maximum amount of information on a peak named {{name}}. I want the precise location and elevation of the peak. Could you also search on Wikidata and Wikipedia for more information?>)
5. Then press yes to accept the ele tag (shown on top of the map)

----

All the links below will work only on MapRoulette, because they use {{mustache}} tags that MapRoulette will replace by data: coordinates of the map or tags of the current shown peak.

Note that I even put a link to directly ask Bing AI all the info about the current peak. So give it a [try](https://maproulette.org/browse/challenges/23309).

### Create the challenge.geojson file

1. Run the python script: `get_peaks.py`
2. Wait around 10 minutes for 4,000 peaks
3. Run the [mr-cli](https://github.com/maproulette/mr-cli) command:

    `mr cooperative tag peaks_with_ele.osm --out challenge.geojson`

Then just import this file when you create or update your challenge in MapRoulette.

#### Details about `get_peaks.py`

1. The script runs an Overpass query to get all peak with tag `wikidata` but without `ele` (elevation) and store them in the file `peak_no_ele.osm`
2. The script start multi-threading on all peaks
3. For each peak, the script make an API call to wikidata to get the elevation of the peak. Then it store the value in the `ele` tag. It also removes the wrong tags `elevation` and `elev`.
4. Then the script save every peaks in a file named peaks_with_ele.osm

My first version of the script was sequential and take around 2 hours for 4,000 peaks, mainly because of the API call.

My second version uses multi-threading and only last 10 minutes for the same number of peaks! 🔥