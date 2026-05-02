import asyncio
import time
from typing import Dict, Optional, Tuple

import httpx


DISTRICT_DEFAULT_COORDS: Dict[str, Tuple[float, float]] = {
    "ariyalur": (11.1385, 79.0756),
    "chennai": (13.0827, 80.2707),
    "chengalpattu": (12.6819, 79.9888),
    "coimbatore": (11.0168, 76.9558),
    "cuddalore": (11.7447, 79.7680),
    "dharmapuri": (12.1211, 78.1582),
    "dindigul": (10.3624, 77.9695),
    "erode": (11.3410, 77.7172),
    "kallakurichi": (11.7384, 78.9639),
    "kanchipuram": (12.8342, 79.7036),
    "kanyakumari": (8.0883, 77.5385),
    "karur": (10.9601, 78.0766),
    "krishnagiri": (12.5186, 78.2137),
    "madurai": (9.9252, 78.1198),
    "mayiladuthurai": (11.1018, 79.6520),
    "nagapattinam": (10.7672, 79.8449),
    "namakkal": (11.2194, 78.1678),
    "nilgiris": (11.4102, 76.6950),
    "perambalur": (11.2333, 78.8833),
    "pudukkottai": (10.3797, 78.8208),
    "ramanathapuram": (9.3639, 78.8395),
    "ranipet": (12.9249, 79.3333),
    "salem": (11.6643, 78.1460),
    "sivaganga": (9.8433, 78.4809),
    "tenkasi": (8.9590, 77.3152),
    "thanjavur": (10.7870, 79.1378),
    "theni": (10.0104, 77.4768),
    "thoothukudi": (8.7642, 78.1348),
    "tiruchirappalli": (10.7905, 78.7047),
    "trichy": (10.7905, 78.7047),
    "tirunelveli": (8.7139, 77.7567),
    "tirupathur": (12.4950, 78.5678),
    "tiruppur": (11.1085, 77.3411),
    "tiruvallur": (13.1439, 79.9089),
    "tiruvannamalai": (12.2253, 79.0747),
    "tiruvarur": (10.7727, 79.6368),
    "vellore": (12.9165, 79.1325),
    "viluppuram": (11.9401, 79.4861),
    "virudhunagar": (9.5851, 77.9579),
}

# In-memory cache for geocoding results
_geo_cache: Dict[str, Tuple[float, float]] = {}

# Rate limiting
_last_request_time = 0
_rate_limit_delay = 1  # 1 second between requests

HEADERS = {"User-Agent": "school-outreach-heatmap/1.0"}


def get_geo_cache() -> Dict[str, Tuple[float, float]]:
  """Get the geocoding cache."""
  return _geo_cache


def clear_geo_cache():
  """Clear the geocoding cache."""
  global _geo_cache
  _geo_cache = {}


def geocode_address(address: str, district: str) -> Tuple[float, float]:
  """Synchronous geocoding with caching."""
  # Try district-level cache first (faster)
  district_key = district.lower()
  if district_key in _geo_cache:
    return _geo_cache[district_key]
  
  # Default coordinates for known districts
  district_coords = DISTRICT_DEFAULT_COORDS.get(district_key)
  if district_coords:
    _geo_cache[district_key] = district_coords
    return district_coords
  
  # Query nominatim for full address
  query = ", ".join(part for part in [address, district, "Tamil Nadu", "India"] if part).strip(", ")
  coords = _query_nominatim(query)
  if coords:
    _geo_cache[district_key] = coords
    return coords
  
  # Default fallback (India center)
  return (12.9716, 77.5946)


def _query_nominatim(query: str) -> Optional[Tuple[float, float]]:
  """Query Nominatim API with rate limiting."""
  if not query:
    return None
  
  global _last_request_time
  
  # Apply rate limiting
  now = time.time()
  time_since_last = now - _last_request_time
  if time_since_last < _rate_limit_delay:
    time.sleep(_rate_limit_delay - time_since_last)
  
  url = "https://nominatim.openstreetmap.org/search"
  params = {"q": query, "format": "json", "limit": 1}

  try:
    response = httpx.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=10
    )
    response.raise_for_status()
    _last_request_time = time.time()
    
    payload = response.json()
    if payload:
      lat = float(payload[0]["lat"])
      lng = float(payload[0]["lon"])
      return (lat, lng)
  except (httpx.HTTPError, ValueError, KeyError) as e:
    print(f"Geocoding error for '{query}': {e}")
    return None

  return None


async def geocode_district_async(district: str) -> Tuple[float, float]:
  """Async geocoding for district name."""
  # Check cache first
  cache_key = district.lower()
  if cache_key in _geo_cache:
    return _geo_cache[cache_key]
  
  # Check defaults
  district_coords = DISTRICT_DEFAULT_COORDS.get(cache_key)
  if district_coords:
    _geo_cache[cache_key] = district_coords
    return district_coords
  
  # Query nominatim
  query = f"{district}, Tamil Nadu, India"
  coords = await _query_nominatim_async(query)
  if coords:
    _geo_cache[cache_key] = coords
    return coords
  
  return (12.9716, 77.5946)


async def _query_nominatim_async(query: str) -> Optional[Tuple[float, float]]:
  """Async Nominatim query with rate limiting."""
  if not query:
    return None
  
  global _last_request_time
  
  # Apply rate limiting
  now = time.time()
  time_since_last = now - _last_request_time
  if time_since_last < _rate_limit_delay:
    await asyncio.sleep(_rate_limit_delay - time_since_last)
  
  url = "https://nominatim.openstreetmap.org/search"
  params = {"q": query, "format": "json", "limit": 1}

  try:
    async with httpx.AsyncClient() as client:
      response = await client.get(
          url,
          headers=HEADERS,
          params=params,
          timeout=10
      )
      response.raise_for_status()
      _last_request_time = time.time()
      
      payload = response.json()
      if payload:
        lat = float(payload[0]["lat"])
        lng = float(payload[0]["lon"])
        return (lat, lng)
  except (httpx.HTTPError, ValueError, KeyError) as e:
    print(f"Async geocoding error for '{query}': {e}")
    return None

  return None
