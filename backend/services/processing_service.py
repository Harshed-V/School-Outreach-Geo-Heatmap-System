import pandas as pd
from utils.geocoding import geocode_address, geocode_district_async
import asyncio


def normalize_district(name):
  """Normalize district name to lowercase."""
  if not isinstance(name, str):
    return "unknown"
  return name.strip().lower()


def _safe_series(df, column, default_value):
  """Get series from dataframe or return default."""
  if column in df.columns:
    return df[column]
  return pd.Series([default_value] * len(df))


def process_school_data(raw_rows):
  """Process and clean school data with batched geocoding."""
  if not raw_rows:
    return pd.DataFrame(columns=["school_name", "district", "address", "type", "lat", "lng"])

  df = pd.DataFrame(raw_rows).copy()
  
  # Clean and normalize data
  df["school_name"] = _safe_series(df, "school_name", "").fillna("").astype(str).str.strip()
  df["district"] = _safe_series(df, "district", "unknown").fillna("unknown").apply(normalize_district)
  df["address"] = _safe_series(df, "address", "").fillna("").astype(str).str.strip()
  df["type"] = _safe_series(df, "type", "private").fillna("private").astype(str).str.strip().str.lower()

  # Remove empty rows
  df = df[df["school_name"] != ""]
  df["district"] = df["district"].replace("", "unknown")
  df["type"] = df["type"].replace("", "private")

  # Remove duplicates based on name + district hash
  df = df.drop_duplicates(subset=["school_name", "district"], keep="first")

  # Batch geocoding by district (more efficient)
  df["lat"], df["lng"] = _batch_geocode_by_district(df)
  
  return df


def _batch_geocode_by_district(df):
  """Batch geocode by district to reduce API calls."""
  # Group by district and cache results
  district_coords = {}
  
  for district in df["district"].unique():
    if district not in district_coords:
      # Cache the first school's address for this district
      district_df = df[df["district"] == district]
      first_address = district_df.iloc[0]["address"]
      coords = geocode_address(first_address, district)
      district_coords[district] = coords
  
  # Map coordinates back to all rows
  lats = df["district"].map(lambda d: district_coords[d][0])
  lngs = df["district"].map(lambda d: district_coords[d][1])
  
  return lats, lngs


async def process_school_data_async(raw_rows):
  """Async version of process_school_data with concurrent geocoding."""
  if not raw_rows:
    return pd.DataFrame(columns=["school_name", "district", "address", "type", "lat", "lng"])

  df = pd.DataFrame(raw_rows).copy()
  
  # Clean and normalize data
  df["school_name"] = _safe_series(df, "school_name", "").fillna("").astype(str).str.strip()
  df["district"] = _safe_series(df, "district", "unknown").fillna("unknown").apply(normalize_district)
  df["address"] = _safe_series(df, "address", "").fillna("").astype(str).str.strip()
  df["type"] = _safe_series(df, "type", "private").fillna("private").astype(str).str.strip().str.lower()

  # Remove empty rows
  df = df[df["school_name"] != ""]
  df["district"] = df["district"].replace("", "unknown")
  df["type"] = df["type"].replace("", "private")

  # Remove duplicates
  df = df.drop_duplicates(subset=["school_name", "district"], keep="first")

  # Async batch geocoding
  district_coords = {}
  unique_districts = df["district"].unique()
  
  # Concurrent geocoding of unique districts
  tasks = [geocode_district_async(district) for district in unique_districts]
  coords_list = await asyncio.gather(*tasks)
  district_coords = dict(zip(unique_districts, coords_list))
  
  # Map coordinates back
  df["lat"] = df["district"].map(lambda d: district_coords[d][0])
  df["lng"] = df["district"].map(lambda d: district_coords[d][1])
  
  return df
