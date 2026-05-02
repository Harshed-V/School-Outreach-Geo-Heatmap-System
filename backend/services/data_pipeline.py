"""
Production-ready data pipeline for School Outreach Geo-Heatmap System.

Handles:
- Loading and normalizing datasets
- Cleaning district names
- Removing duplicates
- Aggregating to district level
- Merging multiple data sources
- Feature engineering
- Scoring model
- Result caching
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

try:
    from scraper.osm_school_fetcher import run_ingestion as fetch_osm, FINAL_OUTPUT_FILE as OSM_FILE
    from scraper.schools_org_scraper import SchoolsOrgScraper
    from services.data_merger import DataMerger
except ImportError:
    pass


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names: strip, lowercase, replace spaces."""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    return df


DISTRICT_ALIAS = {
    "kanniyakumari": "kanyakumari",
    "the nilgiris": "nilgiris",
    "tuticorin": "thoothukudi",
    "trichy": "tiruchirappalli",
    "tiruvallur": "thiruvallur",
    "kancheepuram": "kanchipuram"
}

def normalize_district(df: pd.DataFrame, column: str = "district") -> pd.DataFrame:
    """
    Normalize district names:
    - Lowercase
    - Strip whitespace
    - Remove 'district' keyword
    - Clean extra spaces
    - Apply single source of truth mapping
    """
    if column not in df.columns:
        return df
    
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\bdistrict\b", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.replace("the ", "")
        .str.strip()
    )
    
    # Apply single source of truth alias mapping
    df[column] = df[column].replace(DISTRICT_ALIAS)
    
    return df


def remove_duplicates(df: pd.DataFrame, key_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Remove duplicates with strong deduplication on key fields.
    
    Args:
        df: Input DataFrame
        key_columns: Columns to use for deduplication (default: all unique rows, then key fields)
    
    Returns:
        Deduplicated DataFrame
    """
    # First pass: remove exact duplicates
    df = df.drop_duplicates()
    
    # Second pass: strong dedup based on key fields
    if key_columns and all(col in df.columns for col in key_columns):
        df = df.drop_duplicates(subset=key_columns, keep="first")
    
    return df.reset_index(drop=True)


def normalize(series: pd.Series) -> pd.Series:
    """
    Normalize series to 0-1 range using min-max scaling.
    Handles edge cases (all same values, NaN, etc.)
    """
    min_val = series.min()
    max_val = series.max()
    
    if min_val == max_val:
        return pd.Series([0.5] * len(series), index=series.index)
    
    return (series - min_val) / (max_val - min_val + 1e-6)


# ============================================================================
# DATA LOADING
# ============================================================================

def load_school_dataset(csv_path: str) -> pd.DataFrame:
    """
    Load school_outreach_large_2000plus.csv dataset.
    
    Expected columns (case-insensitive, space-tolerant):
    - District (or variants)
    - No_of_Schools (or variants)
    - Population (optional)
    - Literacy_Rate (optional)
    - Dropout_Rate (optional)
    - Rural_Percentage (optional)
    - Lat, Long (or variants)
    
    Returns:
        Cleaned DataFrame with standardized columns
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"School dataset not found: {csv_path}")
    
    print(f"[LOAD] School dataset: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Clean column names
    df = clean_columns(df)
    
    # Standardize key columns
    df = normalize_district(df, "district")
    
    # Handle latitude/longitude naming variations
    if "long" in df.columns:
        df = df.rename(columns={"long": "lng"})
    
    # Fill missing numeric columns
    numeric_cols = ["population", "no_of_schools", "literacy_rate", "dropout_rate", 
                   "rural_percentage", "lat", "lng"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    
    # Remove duplicates
    key_cols = [col for col in ["district", "no_of_schools", "population"] if col in df.columns]
    df = remove_duplicates(df, key_columns=key_cols)
    
    print(f"[CLEAN] School dataset records: {len(df)}")
    return df


def load_population_dataset(csv_path: str) -> pd.DataFrame:
    """
    Load _TN Population - Sheet1.csv dataset.
    
    Expected columns (case-insensitive):
    - District (or variants)
    - Population (or variants)
    
    Returns:
        Cleaned DataFrame with district and population columns
    """
    if not os.path.exists(csv_path):
        print(f"[WARN] Population dataset not found: {csv_path}")
        return pd.DataFrame()
    
    print(f"[LOAD] Population dataset: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Clean column names
    df = clean_columns(df)
    
    # Normalize district names
    if "district" in df.columns:
        df = normalize_district(df, "district")
    elif "name" in df.columns:
        df = df.rename(columns={"name": "district"})
        df = normalize_district(df, "district")
    
    # Keep only district and population columns
    if "district" in df.columns:
        required_cols = ["district"]
        for col in ["population", "total_population"]:
            if col in df.columns:
                required_cols.append(col)
                break
        
        if len(required_cols) > 1:
            df = df[required_cols].drop_duplicates()
            print(f"[CLEAN] Population dataset records: {len(df)}")
            return df
    
    return pd.DataFrame()


def load_district_metadata(csv_path: str) -> pd.DataFrame:
    """
    Load optional 2015_16_Districtwise.csv for additional metadata.
    
    Returns:
        Cleaned DataFrame with district and additional columns
    """
    if not os.path.exists(csv_path):
        print(f"[WARN] District metadata not found: {csv_path}")
        return pd.DataFrame()
    
    print(f"[LOAD] District metadata: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Clean column names
    df = clean_columns(df)
    
    # Normalize district names - check for DISTNAME column (2015-16 format)
    if "distname" in df.columns:
        df = df.rename(columns={"distname": "district"})
    
    if "district" in df.columns:
        df = normalize_district(df, "district")
        print(f"[CLEAN] District metadata records: {len(df)}")
        return df
    
    return pd.DataFrame()


# ============================================================================
# DATA AGGREGATION
# ============================================================================

def aggregate_to_district_level(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate school dataset to district level.
    
    Aggregation functions:
    - no_of_schools: sum
    - population: sum (or mean if already aggregated)
    - literacy_rate: mean
    - dropout_rate: mean
    - rural_percentage: mean
    - lat, lng: mean (geographic center)
    
    Returns:
        District-level aggregated DataFrame
    """
    if len(df) == 0:
        return pd.DataFrame()
    
    if "district" not in df.columns:
        raise ValueError("'district' column required for aggregation")
    
    agg_dict = {"district": "first"}  # Keep district name
    
    # Aggregate numeric columns
    numeric_cols = {
        "population": "sum",
        "no_of_schools": "sum",
        "literacy_rate": "mean",
        "dropout_rate": "mean",
        "rural_percentage": "mean",
        "lat": "mean",
        "lng": "mean",
    }
    
    for col, func in numeric_cols.items():
        if col in df.columns:
            agg_dict[col] = func
    
    district_df = df.groupby("district", as_index=False).agg(agg_dict)
    print(f"[AGGREGATE] Districts: {len(district_df)}")
    return district_df


# ============================================================================
# DATA MERGING
# ============================================================================

def merge_datasets(
    school_df: pd.DataFrame,
    population_df: Optional[pd.DataFrame] = None,
    metadata_df: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Merge school, population, and optional metadata datasets.
    
    Strategy:
    - Start with aggregated school data
    - Left merge with population (fallback to school dataset's population)
    - Left merge with metadata (optional)
    - Resolve population conflicts
    
    Returns:
        Merged district-level DataFrame
    """
    merged = school_df.copy()
    
    # Merge population data
    if population_df is not None and len(population_df) > 0:
        pop_cols = [col for col in ["population", "total_population"] if col in population_df.columns]
        if pop_cols:
            pop_rename = {pop_cols[0]: "population_from_pop_dataset"}
            population_df = population_df.rename(columns=pop_rename)
            
            merged = merged.merge(
                population_df,
                on="district",
                how="left"
            )
            
            # Prefer population from dedicated dataset, fallback to school dataset
            if "population_from_pop_dataset" in merged.columns:
                merged["population"] = (
                    merged["population_from_pop_dataset"]
                    .fillna(merged["population"])
                )
                merged = merged.drop(columns=["population_from_pop_dataset"])
    
    # Merge metadata
    if metadata_df is not None and len(metadata_df) > 0:
        # Metadata might have different district column names (e.g., DISTNAME)
        meta_df = metadata_df.copy()
        
        # Rename common district column variants
        if "distname" in meta_df.columns:
            meta_df = meta_df.rename(columns={"distname": "district"})
        elif "district_name" in meta_df.columns:
            meta_df = meta_df.rename(columns={"district_name": "district"})
        
        # Normalize district names in metadata
        if "district" in meta_df.columns:
            meta_df = normalize_district(meta_df, "district")
            
            # Select non-overlapping columns from metadata
            meta_cols = [col for col in meta_df.columns 
                        if col not in merged.columns or col == "district"]
            
            if "district" in meta_cols and len(meta_cols) > 1:
                meta_df = meta_df[meta_cols]
                merged = merged.merge(
                    meta_df,
                    on="district",
                    how="left"
                )
    
    print(f"[MERGE] Final district records: {len(merged)}")
    return merged


# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create derived features for scoring model.
    
    Features:
    - school_density: no_of_schools / (population + 1)
    - literacy_factor: literacy_rate (already 0-100)
    - dropout_factor: 100 - dropout_rate (invert for scoring)
    - urban_factor: 100 - rural_percentage (invert for scoring)
    
    Returns:
        DataFrame with engineered features
    """
    df = df.copy()
    
    # School density: schools per capita
    if "no_of_schools" in df.columns and "population" in df.columns:
        df["school_density"] = df["no_of_schools"] / (df["population"] + 1)
    else:
        df["school_density"] = 0.0
    
    # Literacy factor: use as-is (0-100)
    if "literacy_rate" in df.columns:
        df["literacy_factor"] = df["literacy_rate"].fillna(0)
    else:
        df["literacy_factor"] = 0.0
    
    # Dropout factor: invert so lower dropout = higher score
    if "dropout_rate" in df.columns:
        df["dropout_factor"] = 100 - df["dropout_rate"].fillna(0)
    else:
        df["dropout_factor"] = 50.0
    
    # Urban factor: invert rural percentage
    if "rural_percentage" in df.columns:
        df["urban_factor"] = 100 - df["rural_percentage"].fillna(0)
    else:
        df["urban_factor"] = 50.0
    
    print(f"[FEATURES] Engineered features for {len(df)} districts")
    return df


# ============================================================================
# SCORING MODEL
# ============================================================================

def score_districts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply production scoring model to districts.
    
    Weights:
    - 0.30: Number of schools (normalized)
    - 0.20: School density (normalized)
    - 0.20: Literacy factor (normalized)
    - 0.15: Dropout factor (normalized)
    - 0.15: Urban factor (normalized)
    
    Score range: 0-100
    
    Returns:
        DataFrame with 'score' column (0-100)
    """
    if len(df) == 0:
        return df
    
    df = df.copy()
    
    # Ensure all features exist
    required_features = ["school_density", "literacy_factor", "dropout_factor", "urban_factor"]
    for feat in required_features:
        if feat not in df.columns:
            df[feat] = 0.0
    
    # Normalize features
    norm_schools = normalize(df["no_of_schools"]) if "no_of_schools" in df.columns else pd.Series([0.5] * len(df))
    norm_density = normalize(df["school_density"])
    norm_literacy = normalize(df["literacy_factor"])
    norm_dropout = normalize(df["dropout_factor"])
    norm_urban = normalize(df["urban_factor"])
    
    # Apply weighted scoring
    df["score"] = (
        0.30 * norm_schools +
        0.20 * norm_density +
        0.20 * norm_literacy +
        0.15 * norm_dropout +
        0.15 * norm_urban
    ) * 100
    
    # Ensure score is in valid range
    df["score"] = df["score"].clip(0, 100).round(2)
    
    print(f"[SCORE] Scored {len(df)} districts | Score range: {df['score'].min():.0f}-{df['score'].max():.0f}")
    return df


# ============================================================================
# FINAL OUTPUT & CACHING
# ============================================================================

def prepare_final_output(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare final output for API: select and rename key columns.
    
    Output columns:
    - district: district name (title case)
    - schools: number of schools
    - score: outreach potential score (0-100)
    - lat: latitude of district center
    - lng: longitude of district center
    
    Returns:
        Final DataFrame with API-ready columns
    """
    output_cols = ["district", "no_of_schools", "score", "lat", "lng"]
    available_cols = [col for col in output_cols if col in df.columns]
    
    final = df[available_cols].copy()
    
    # Rename for API
    final = final.rename(columns={
        "no_of_schools": "schools",
    })
    
    # Ensure district is title case
    if "district" in final.columns:
        final["district"] = final["district"].str.title()
    
    # Fill missing coordinates
    final["lat"] = final["lat"].fillna(0.0)
    final["lng"] = final["lng"].fillna(0.0)
    
    # Ensure correct dtypes
    final["schools"] = final["schools"].fillna(0).astype(int)
    final["score"] = final["score"].fillna(0).astype(float)
    final["lat"] = final["lat"].astype(float)
    final["lng"] = final["lng"].astype(float)
    
    return final


def cache_results(final_df: pd.DataFrame) -> List[Dict]:
    """
    Convert final DataFrame to cache format (list of dicts).
    
    Returns:
        List of district records ready for API serialization
    """
    return final_df.to_dict(orient="records")


from utils.download_data import download_if_missing

# ============================================================================
# MAIN PIPELINE ORCHESTRATOR
# ============================================================================

def run_data_pipeline(
    school_csv_path: str,
    population_csv_path: Optional[str] = None,
    metadata_csv_path: Optional[str] = None,
    use_osm: bool = False,
    use_scraper: bool = False
) -> Tuple[List[Dict], Dict]:
    """
    Execute complete production data pipeline.
    """
    # Ensure dataset exists before starting
    download_if_missing(school_csv_path)

    stats = {
        "school_records": 0,
        "population_records": 0,
        "metadata_records": 0,
        "districts": 0,
        "score_range": (0, 0),
    }
    
    try:
        print("\n" + "=" * 70)
        print("PRODUCTION DATA PIPELINE")
        print("=" * 70)
        
        # 1. LOAD DATASETS
        print("\n[STAGE 1] LOADING DATASETS")
        print("-" * 70)
        school_df = load_school_dataset(school_csv_path)
        stats["school_records"] = len(school_df)
        
        population_df = None
        if population_csv_path:
            population_df = load_population_dataset(population_csv_path)
            stats["population_records"] = len(population_df)
        
        metadata_df = None
        if metadata_csv_path:
            metadata_df = load_district_metadata(metadata_csv_path)
            stats["metadata_records"] = len(metadata_df)
        
        # 2. AGGREGATE TO DISTRICT LEVEL
        print("\n[STAGE 2] AGGREGATING TO DISTRICT LEVEL (HYBRID)")
        print("-" * 70)
        district_df = aggregate_to_district_level(school_df)
        
        # HYBRID INGESTION
        if use_osm or use_scraper:
            print(f"[HYBRID] Running external fetchers... OSM={use_osm}, SCRAPER={use_scraper}")
            merger = DataMerger()
            merger.load_csv(school_csv_path)
            
            if use_osm:
                try:
                    fetch_osm()
                    merger.load_json(OSM_FILE)
                except Exception as e:
                    print(f"[HYBRID ERROR] OSM Fetcher failed: {e}")
                    
            if use_scraper:
                try:
                    scraper = SchoolsOrgScraper()
                    scraper.run()
                    merger.load_json('schools_org_in_data.json')
                except Exception as e:
                    print(f"[HYBRID ERROR] Schools scraper failed: {e}")
            
            hybrid_results = merger.process()
            hybrid_df = pd.DataFrame(hybrid_results)
            
            if not hybrid_df.empty:
                hybrid_df = hybrid_df.rename(columns={"count": "no_of_schools"})
                if "no_of_schools" in district_df.columns:
                    district_df = district_df.drop(columns=["no_of_schools"])
                district_df = district_df.merge(
                    hybrid_df[["district", "no_of_schools"]], 
                    on="district", 
                    how="left"
                )
                district_df["no_of_schools"] = district_df["no_of_schools"].fillna(0)
                print(f"[HYBRID] Successfully unified counts with deduplication logic.")
        
        # 3. MERGE DATASETS
        print("\n[STAGE 3] MERGING DATASETS")
        print("-" * 70)
        merged_df = merge_datasets(district_df, population_df, metadata_df)
        
        # 4. ENGINEER FEATURES
        print("\n[STAGE 4] FEATURE ENGINEERING")
        print("-" * 70)
        features_df = engineer_features(merged_df)
        
        # 5. APPLY SCORING MODEL
        print("\n[STAGE 5] SCORING MODEL")
        print("-" * 70)
        scored_df = score_districts(features_df)
        
        # 6. PREPARE FINAL OUTPUT
        print("\n[STAGE 6] PREPARING FINAL OUTPUT")
        print("-" * 70)
        final_df = prepare_final_output(scored_df)
        
        # 7. CACHE RESULTS
        print("\n[STAGE 7] CACHING RESULTS")
        print("-" * 70)
        cached = cache_results(final_df)
        
        # Update statistics
        stats["districts"] = len(final_df)
        stats["score_range"] = (
            float(final_df["score"].min()),
            float(final_df["score"].max()),
        )
        
        print(f"[CACHE] {len(cached)} districts cached for API")
        
        print("\n" + "=" * 70)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"Districts: {stats['districts']}")
        print(f"Score range: {stats['score_range'][0]:.0f} - {stats['score_range'][1]:.0f}")
        print("=" * 70 + "\n")
        
        return cached, stats
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    # Test the pipeline
    from utils.config import SCHOOL_DATASET_PATH
    
    school_path = SCHOOL_DATASET_PATH
    pop_path = os.path.join(os.path.dirname(school_path), "_TN Population  - Sheet1.csv")
    metadata_path = os.path.join(os.path.dirname(school_path), "2015_16_Districtwise.csv")
    
    cached, stats = run_data_pipeline(school_path, pop_path, metadata_path)
    print(f"\nSample districts (top 5):")
    for district in cached[:5]:
        print(f"  {district['district']}: {district['score']:.0f} | {district['schools']} schools")
