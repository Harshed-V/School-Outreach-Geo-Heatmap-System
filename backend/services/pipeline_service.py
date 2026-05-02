import os
from typing import Dict, List

from utils.config import (
    SCHOOL_DATASET_PATH,
    POPULATION_DATASET_PATH,
    METADATA_DATASET_PATH,
)


# Global cache for district data
_data_cache = None
_cache_stats = None


def run_pipeline(
    school_path: str = None,
    population_path: str = None,
    metadata_path: str = None,
    use_osm: bool = None,
    use_scraper: bool = None
) -> Dict:
  """
  Production data pipeline: Load, clean, aggregate, merge, score, cache.
  
  Loads datasets in order:
    1. school_outreach_large_2000plus.csv (required)
    2. _TN Population - Sheet1.csv (optional)
    3. 2015_16_Districtwise.csv (optional)
  
  Returns pipeline status and statistics.
  """
  global _data_cache, _cache_stats
  
  school_path = school_path or SCHOOL_DATASET_PATH
  population_path = population_path or POPULATION_DATASET_PATH
  metadata_path = metadata_path or METADATA_DATASET_PATH
  
  # Flags for hybrid data pipeline (Step 16)
  if use_osm is None:
      use_osm = os.getenv("USE_OSM", "True").lower() == "true"
  if use_scraper is None:
      use_scraper = os.getenv("USE_SCRAPER", "True").lower() == "true"
  
  from utils.download_data import download_if_missing
  
  try:
    # Ensure dataset exists before starting
    download_if_missing(school_path)
    
    if not os.path.exists(school_path):
      raise FileNotFoundError(
          f"School dataset CSV not found: {school_path}. "
          "Please check your internet connection for auto-download or place schools.csv in data/."
      )
    
    from services.data_pipeline import run_data_pipeline
    
    print(f"[PIPELINE] Starting production data pipeline... (OSM={use_osm}, SCRAPER={use_scraper})")
    cached, stats = run_data_pipeline(
        school_path, 
        population_path, 
        metadata_path,
        use_osm=use_osm,
        use_scraper=use_scraper
    )
    
    # Cache in memory for API
    _data_cache = cached
    _cache_stats = stats
    
    # Build response
    response = {
        "status": "success",
        "message": "Production data pipeline completed successfully",
        "districts_count": stats["districts"],
        "score_range": stats["score_range"],
        "sample_districts": cached[:5] if cached else [],
        "statistics": {
            "school_records_processed": stats["school_records"],
            "population_records_loaded": stats["population_records"],
            "metadata_records_loaded": stats["metadata_records"],
            "final_districts": stats["districts"],
        },
    }
    
    print(f"[PIPELINE] Pipeline completed: {response['message']}")
    return response
    
  except Exception as e:
    print(f"[ERROR] Pipeline failed: {e}")
    return {
        "status": "error",
        "message": str(e),
        "school_path": school_path,
    }


def get_cached_districts() -> List[Dict]:
  """
  Retrieve cached district data for API.
  
  Returns:
    List of districts with scores and coordinates. If cache is empty,
    runs pipeline first.
  """
  global _data_cache
  
  if _data_cache is None:
    print("[CACHE] Cache miss - running pipeline to populate cache...")
    run_pipeline()
  
  return _data_cache or []


def get_cache_stats() -> Dict:
  """Get pipeline statistics from last run."""
  global _cache_stats
  return _cache_stats or {}


def refresh_cache() -> Dict:
  """Refresh cached data by re-running the pipeline."""
  return run_pipeline()


async def run_pipeline_async() -> Dict:
  """Async-compatible wrapper for existing callers."""
  return run_pipeline()
