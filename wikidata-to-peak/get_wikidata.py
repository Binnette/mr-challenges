import requests
import time
import json
import math
import multiprocessing
import numpy
import xml.etree.ElementTree as ET
from os import path
from tqdm import tqdm
from urllib.parse import unquote

# wget https://overpass-api.de/api/interpreter?data=node%5B%22natural%22%3D%22peak%22%5D%5B%22name%22%5D%5B%21%22wikidata%22%5D%3Bout%20meta%3B -O peaks_overpass.osm
# Define the Overpass API URL and query
over_url = "https://overpass-api.de/api/interpreter"
over_query = """
node[natural=peak][name][!wikidata];
out meta;
"""

# Define the output file names
over_file = "peaks_overpass.osm"
wiki_json = "wikidata_response.json"

# Define the Wikidata SPARQL endpoint URL and query template
wikidata_url = "https://query.wikidata.org/sparql"
query_prefix = ('SELECT ?id ?item ?itemLabel ?elevation ?article ?coordinate WHERE {'
                'VALUES (?id ?mountainName) {')
query_suffix = ('}'
                ' ?item rdfs:label ?mountainName .'
                ' ?item wdt:P31 wd:Q8502 .'
                ' ?item wdt:P2044 ?elevation .'
                ' ?article schema:about ?item .'
                ' ?article schema:isPartOf <https://en.wikipedia.org/> .'
                ' ?item wdt:P625 ?coordinate .'
                ' SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }'
                '}')

def distance_in_meters(latitude1, longitude1, latitude2, longitude2):
    # Convert degrees to radians
    latitude1 = math.radians(latitude1)
    longitude1 = math.radians(longitude1)
    latitude2 = math.radians(latitude2)
    longitude2 = math.radians(longitude2)

    # Calculate the differences
    delta_latitude = latitude2 - latitude1
    delta_longitude = longitude2 - longitude1

    # Apply the haversine formula
    a = math.sin(delta_latitude / 2) ** 2 + math.cos(latitude1) * math.cos(latitude2) * math.sin(delta_longitude / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371000 # Earth radius in meters
    d = r * c # Distance in meters

    return d

# Define a function to get the Wikidata results for a given query
def getWikidataResult(peaks, calls):
    print(f"Call query.wikidata.org {calls}")

    query = query_prefix + "".join(peaks) + query_suffix

    # Use a POST request with the query and format parameters in the data
    result = requests.post(wikidata_url, data={'query': query, 'format': 'json'})

    while result.status_code == 429:
        # Too many requests.
        print("Got error 429: wait 1s")
        time.sleep(1)
        result = requests.post(wikidata_url, data={'query': query, 'format': 'json'})

    if result.status_code == 500 and "TimeoutException" in result.text:
        print("TimeoutException. Try splitting query in 2")
        chunks = numpy.array_split(peaks, 2)
        res1 = getWikidataResult(chunks[0], calls)
        res2 = getWikidataResult(chunks[1], calls)
        return res1 + res2

    if result.status_code == 502:
        print("Error 502. Wikidata server seems to be down.")
        return

    if result.status_code != 200:
        print(f"Error code {result.status_code} for the query:")
        print(f"{query}")
        return

    res = result.json()
    return res['results']['bindings']

# Define a function to query Wikidata for all the peaks in the Overpass data
def queryWikidata():
    data = []
    query = []
    calls = 0
    print("Create wikidata query")
    
    # Use a for loop instead of a while loop
    for node in tree.findall('node'):
        node_id = node.get('id')
        name_tag = node.find("tag[@k='name']")
        if name_tag is not None:
            node_name = name_tag.get('v').replace('"', '')
            query.append(f'({node_id} "{node_name}"@en)')

        # Use a constant instead of a magic number
        if len(query) > 10000:
            res = getWikidataResult(query, calls)
            calls += 1
            data += res
            query = []

    res = getWikidataResult(query, calls)
    data += res
    query = ""

    print("Dump results in res.json")
    with open(wiki_json, mode="w") as f:
        json.dump(data, f, indent=2)

    return data

def count_modified_nodes(tree):
    count = 0
    for node in tree.findall('node'):
        if node.get('action') == 'modify':
            count += 1
    return count

def process_node(node):
    try:
        # Use the get method with a default value instead of finding the tag and checking for None
        node_name = node.find("tag[@k='name']").get('v', '')
        
        # Skip the node if there is no name tag
        if not node_name:
            return node

        node_id = node.get('id')
        lat = float(node.get('lat'))
        lon = float(node.get('lon'))

        # Use a list comprehension to filter the Wikidata data by node id
        items = [res for res in data if node_id == res['id']['value']]

        # Skip the node if there is no Wikidata result
        if not items:
            return node

        # Use the first element of the list as the result
        item = items[0]
        coordinate_value = item['coordinate']['value']  
        coordinate_value = coordinate_value.replace("Point(", "").replace(")", "")
        # Split the string by space and assign the two values to variables wiki_lat and wiki_lon
        wiki_lon, wiki_lat = coordinate_value.split()
        wiki_lon = float(wiki_lon) 
        wiki_lat = float(wiki_lat) 
        
        distance = distance_in_meters(lat, lon, wiki_lat, wiki_lon)
        if distance > 100:
            return node
        
        node.set("action", "modify")

        item_uri = item['item']['value']
        item_label = item['itemLabel']['value']
        elevation_value = item['elevation']['value']
        article_url = item['article']['value']

        wikidata = item_uri.split("/")[-1]
        ET.SubElement(node, "tag", {"k": "wikidata", "v": wikidata})

        article = "en:" + article_url.replace("https://en.wikipedia.org/wiki/", "").replace("_", " ")
        article = unquote(article)
        ET.SubElement(node, "tag", {"k": "wikipedia", "v": article})
        return node
    except Exception as e:
        print(e)
        return node

# Query Overpass if the output file does not exist
if not path.exists(over_file):
    print("Query Overpass to get all peaks without wikidata. Be patient...")
    
    # Use a GET request with the data parameter in the params
    result = requests.get(over_url, params={'data': over_query})
    with open(over_file, "wb") as f:
        f.write(result.content)
else:
    print(f"Reuse file {over_file} for the list of peaks without wikidata")

tree = ET.parse(over_file)

# Query Wikidata if the output file does not exist
if not path.exists(wiki_json):
    print("Query Wikidata for each peaks name. Be patient...")
    data = queryWikidata()
else:
    print(f"Reuse file {wiki_json} to read peaks found on wikidata")
    with open(wiki_json, "r") as f:
        data = json.load(f)

root = tree.getroot()
nodes = root.findall("node")

print("Run multiprocessing")

# Create a pool of workers with the same number of CPU cores
pool = multiprocessing.Pool(16)
# Wrap the pool.imap generator with tqdm and pass the total argument as len(nodes)
results = tqdm(pool.imap(process_node, nodes), total=len(nodes))
# Replace the original nodes with the modified ones
for i, node in enumerate(results):
    root[i] = node

peaks_to_modify = count_modified_nodes(tree)

tree.write("all_peaks.osm", encoding="UTF-8", xml_declaration=True)

print(f'File written: all_peaks.osm')

# Create a new root element for the output file
new_root = ET.Element('osm', root.attrib)

# Loop through the nodes in the input file
for node in root.findall('node'):
  # Check if the node has the action attribute set to modify
  if node.get('action') == 'modify':
    # Copy the node and append it to the new root element
    new_node = ET.SubElement(new_root, 'node', node.attrib)
    for tag in node.findall('tag'):
      # Copy the tag and append it to the new node element
      new_tag = ET.SubElement(new_node, 'tag', tag.attrib)

# Create a new tree with the new root element
new_tree = ET.ElementTree(new_root)

# Write the output file
new_tree.write('peaks_with_changes.osm', encoding="UTF-8", xml_declaration=True)

print(f'Peak to modify: {peaks_to_modify}. File written: peaks_with_changes.osm')
