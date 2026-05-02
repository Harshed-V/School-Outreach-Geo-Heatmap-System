import requests
import time
import json
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Files for caching
FINAL_OUTPUT_FILE = 'osm_schools_data.json'
GEOCODE_CACHE_FILE = 'geocode_cache.json'

def fetch_osm_schools():
    url = "https://overpass-api.de/api/interpreter"
    query = """
    [out:json][timeout:25];
    area["name"="Tamil Nadu"]->.a;
    node["amenity"="school"](area.a);
    out;
    """
    logger.info("Fetching schools from OSM via Overpass API...")
    try:
        response = requests.post(url, data={'data': query}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Overpass API: {e}")
        return {}

def load_cache(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Corrupt cache file {filepath}. Starting fresh.")
    return {}

def save_cache(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def reverse_geocode(lat, lon, cache):
    """
    Reverse geocodes a lat/lon to a district.
    Uses spatial caching (rounding to 2 decimal places) to massively reduce API calls.
    """
    # Round to 2 decimal places (~1.1 km resolution)
    # This groups nearby schools to share the same district lookup, avoiding thousands of identical API calls
    coord_key = f"{round(lat, 2)},{round(lon, 2)}"
    
    if coord_key in cache:
        return cache[coord_key]
    
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'zoom': 10 # Zoom 10 usually corresponds to city/district level
    }
    headers = {
        # Nominatim requires a valid user-agent
        'User-Agent': 'SchoolOutreachDataIngestion/1.0 (admin@example.com)'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        address = data.get('address', {})
        
        # Districts could be stored under different keys depending on the region
        district = (address.get('state_district') or 
                    address.get('county') or 
                    address.get('district') or 
                    address.get('city') or 
                    'Unknown')
        
        if district.lower().endswith(' district'):
            district = district[:-9] # clean up " District" suffix
            
        cache[coord_key] = district
        save_cache(cache, GEOCODE_CACHE_FILE)
        
        # RATE LIMITING (Crucial for Nominatim: Max 1 request per second)
        logger.debug(f"Geocoded new location {lat}, {lon} -> {district}. Sleeping for 1.1s...")
        time.sleep(1.1) 
        
        return district
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error reverse geocoding {lat}, {lon}: {e}")
        time.sleep(5) # Back off on error
        return 'Unknown'
    except Exception as e:
        logger.error(f"Unexpected error reverse geocoding {lat}, {lon}: {e}")
        return 'Unknown'

def run_ingestion():
    # 1. Fetch data from OpenStreetMap
    osm_data = fetch_osm_schools()
    nodes = osm_data.get('elements', [])
    
    if not nodes:
        logger.error("No schools fetched. Exiting.")
        return
        
    logger.info(f"Successfully fetched {len(nodes)} schools.")
    
    # 2. Load Geocode cache to avoid redundant Nominatim API hits
    geocode_cache = load_cache(GEOCODE_CACHE_FILE)
    logger.info(f"Loaded {len(geocode_cache)} cached geocode coordinates.")
    
    results = []
    
    # 3. Process each school
    for idx, node in enumerate(nodes):
        lat = node.get('lat')
        lon = node.get('lon')
        tags = node.get('tags', {})
        
        name = tags.get('name')
        if not name:
            continue # Skip nodes without a name
            
        if idx % 100 == 0:
            logger.info(f"Processing school {idx}/{len(nodes)}...")
            
        district = reverse_geocode(lat, lon, geocode_cache)
        
        results.append({
            "name": name,
            "district": district,
            "lat": lat,
            "lng": lon
        })
        
    # 4. Save final output
    save_cache(results, FINAL_OUTPUT_FILE)
    logger.info(f"Ingestion complete. Saved {len(results)} valid schools to {FINAL_OUTPUT_FILE}.")

if __name__ == "__main__":
    run_ingestion()
