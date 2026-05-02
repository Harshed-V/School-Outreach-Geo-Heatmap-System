import requests
import time
import logging

logger = logging.getLogger(__name__)

class ReverseGeocodingService:
    def __init__(self):
        self.geo_cache = {}
        self.url = "https://nominatim.openstreetmap.org/reverse"
        self.headers = {
            'User-Agent': 'SchoolOutreachGeoService/1.0 (contact@example.com)'
        }

    def get_district(self, lat, lon):
        """
        Reverse geocodes a latitude and longitude to find the district.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            str: The extracted district name, or "unknown" if not found.
        """
        # Ensure lat/lon are floats for consistent cache keys
        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            return "unknown"

        coord_key = (lat, lon)
        
        # 5. Avoid duplicate calls
        if coord_key in self.geo_cache:
            return self.geo_cache[coord_key]

        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'zoom': 10  # Zoom level 10 maps roughly to city/district
        }

        try:
            # 1. & 2. Use Nominatim API with lat, lon input
            response = requests.get(self.url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            address = data.get('address', {})
            
            # 3. Extract district / state_district
            district = (address.get('state_district') or 
                        address.get('district') or 
                        address.get('county') or 
                        address.get('city') or 
                        'unknown')

            # Clean up the string if it contains " District"
            if district.lower().endswith(' district'):
                district = district[:-9]

            # 4. Cache results
            self.geo_cache[coord_key] = district
            
            # 6. Add delay (Nominatim requires max 1 req/sec)
            time.sleep(1)
            
            return district

        except requests.exceptions.RequestException as e:
            logger.error(f"Network/API error for {lat}, {lon}: {e}")
            # 7. Handle failures
            return "unknown"
        except Exception as e:
            logger.error(f"Unexpected error geocoding {lat}, {lon}: {e}")
            # 7. Handle failures
            return "unknown"

# Singleton instance for easy importing and shared cache
geocoder = ReverseGeocodingService()
