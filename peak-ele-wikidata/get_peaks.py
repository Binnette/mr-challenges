import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm
import multiprocessing

# France only
overpass_url = 'http://overpass-api.de/api/interpreter?data=area%5B%22name%22%3D%22France%22%5D%2D%3E%2Ea%3Bnode%5B%22natural%22%3D%22peak%22%5D%5B%22wikidata%22%5D%5B%22ele%22%21%7E%22%2E%2A%22%5D%28area%2Ea%29%3Bout%20meta%3B%0A'
# area[name="France"]->.a;
# node[natural=peak][wikidata][!ele](area.a);
# out meta;

# World
overpass_url = 'http://overpass-api.de/api/interpreter?data=node%5B%22natural%22%3D%22peak%22%5D%5B%22wikidata%22%5D%5B%22ele%22%21%7E%22%2E%2A%22%5D%3Bout%20meta%3B%0A'
# node[natural=peak][wikidata][!ele];
# out meta;

# Download the data and save it in a file named peaks_no_ele.osm
response = requests.get(overpass_url)
with open("peaks_no_ele.osm", "wb") as f:
    f.write(response.content)

def get_ele_from_wikidata(wikidata_id):
    elevation = None
    # Make a GET request to the wikidata url and store the response
    response = requests.get(f'https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json')
    try:
        wikidata_data = response.json()
        # Get the elevation value from the JSON data using a nested get method
        ele = wikidata_data.get("entities", {}).get(wikidata_id, {}).get("claims", {}).get("P2044", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("amount", None)
        # If the elevation value exists, remove the '+' sign and convert it to a float
        if ele:
            elevation = ele.replace("+", "")
    except:
        pass # ignore the exception and proceed
    return elevation

def delete_invalid_ele_tags(node):
  # Find all the tag elements in the XML
  tags = node.findall('tag')
  # Loop through the list of tags
  for tag in tags:
    # Get the value of the k attribute of the tag
    k = tag.get('k')
    # If the value of k is 'elevation' or 'ele', delete the tag from the XML
    if k == 'elevation' or k == 'elev':
      node.remove(tag)

def process_node(node):
    # Get the child <tag k="wikidata">
    wikidata = node.find("tag[@k='wikidata']")
    # If the tag exists, get the value in the prop "v"
    if wikidata is not None:
        wikidata_id = wikidata.get("v")
        # Get Elevation from Wikidata
        elevation = get_ele_from_wikidata(wikidata_id)
        if elevation:
            # Add a new child <tag k="ele" v="{ele}">
            ET.SubElement(node, "tag", {"k": "ele", "v": elevation})
            # Add the property action='modify' to the parent node
            node.set("action", "modify")
            # Delete invalid elevation and elev tags
            delete_invalid_ele_tags(node)
    return node

def count_ele_tags(tree):
  # Find all the node elements in the XML
  nodes = tree.findall("node")
  # Initialize a counter for the number of tags
  count = 0
  # Loop through the list of nodes
  for node in nodes:
    # Find all the tag elements with attribute k='ele' within each node
    tags = node.findall("tag[@k='ele']")
    # Add the length of the list of tags to the counter
    count += len(tags)
  # Return the final count
  return count

# Parse the xml file and get the root element
tree = ET.parse("peaks_no_ele.osm")
root = tree.getroot()
nodes = root.findall("node")

# Create a pool of workers with the same number of CPU cores
pool = multiprocessing.Pool()
# Wrap the pool.imap generator with tqdm and pass the total argument as len(nodes)
results = tqdm(pool.imap(process_node, nodes), total=len(nodes))
# Replace the original nodes with the modified ones
for i, node in enumerate(results):
    root[i] = node

# Count the peaks to modify
peaks_to_modify = count_ele_tags(tree)

# Save the modified xml to a file named "peaks_with_ele.osm"
tree.write("peaks_with_ele.osm")

print(f'Peak to modify: {peaks_to_modify}. File written: peaks_with_ele.osm')
