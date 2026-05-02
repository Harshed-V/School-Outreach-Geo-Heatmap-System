#!/usr/bin/env python3
"""
Test suite for production data pipeline.

Tests:
- Data loading and validation
- Column cleaning and normalization
- District name normalization
- Deduplication
- Aggregation
- Merging
- Feature engineering
- Scoring model
- Output formatting
- Caching
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import (
    SCHOOL_DATASET_PATH,
    POPULATION_DATASET_PATH,
    METADATA_DATASET_PATH,
)
from services.data_pipeline import (
    clean_columns,
    normalize_district,
    remove_duplicates,
    normalize,
    load_school_dataset,
    load_population_dataset,
    load_district_metadata,
    aggregate_to_district_level,
    merge_datasets,
    engineer_features,
    score_districts,
    prepare_final_output,
    cache_results,
    run_data_pipeline,
)
import pandas as pd


def test_clean_columns():
    """Test column name cleaning."""
    print("\n[TEST] Column cleaning...")
    df = pd.DataFrame({
        " District ": ["Chennai", "Madurai"],
        "NO_OF_SCHOOLS": [100, 50],
        "Literacy Rate": [85.0, 75.0],
        "Rural-Percentage": [25, 45],
    })
    
    cleaned = clean_columns(df)
    expected_cols = {"district", "no_of_schools", "literacy_rate", "rural_percentage"}
    actual_cols = set(cleaned.columns)
    
    assert expected_cols == actual_cols, f"Expected {expected_cols}, got {actual_cols}"
    print("   ✓ Column names cleaned: spaces, hyphens, case normalized")


def test_normalize_district():
    """Test district name normalization."""
    print("\n[TEST] District normalization...")
    df = pd.DataFrame({
        "district": [
            "  Chennai  ",
            "District Madurai",
            "COIMBATORE DISTRICT",
            "salem",
        ]
    })
    
    normalized = normalize_district(df)
    expected = ["chennai", "madurai", "coimbatore", "salem"]
    actual = normalized["district"].tolist()
    
    assert expected == actual, f"Expected {expected}, got {actual}"
    print("   ✓ Districts normalized: lowercase, stripped, 'district' removed")


def test_remove_duplicates():
    """Test deduplication logic."""
    print("\n[TEST] Deduplication...")
    df = pd.DataFrame({
        "district": ["Chennai", "Chennai", "Madurai", "Madurai"],
        "schools": [100, 100, 50, 51],
        "population": [5000000, 5000000, 1500000, 1500000],
    })
    
    deduped = remove_duplicates(df, key_columns=["district", "schools", "population"])
    assert len(deduped) == 3, f"Expected 3 rows, got {len(deduped)}"
    print("   ✓ Duplicates removed: exact matches and key-field matches")


def test_normalize_function():
    """Test min-max normalization."""
    print("\n[TEST] Min-max normalization...")
    series = pd.Series([0, 50, 100])
    normalized = normalize(series)
    
    expected = [0.0, 0.5, 1.0]
    actual = normalized.tolist()
    
    for exp, act in zip(expected, actual):
        assert abs(exp - act) < 0.01, f"Expected {exp}, got {act}"
    print("   ✓ Series normalized to 0-1 range")


def test_load_school_dataset():
    """Test school dataset loading."""
    print("\n[TEST] School dataset loading...")
    
    if not os.path.exists(SCHOOL_DATASET_PATH):
        print("   ⚠ School dataset not found, skipping")
        return
    
    df = load_school_dataset(SCHOOL_DATASET_PATH)
    
    assert len(df) > 0, "No data loaded"
    assert "district" in df.columns, "Missing 'district' column"
    print(f"   ✓ Loaded {len(df)} school records")
    print(f"   ✓ Columns: {list(df.columns)[:5]}...")


def test_load_population_dataset():
    """Test population dataset loading."""
    print("\n[TEST] Population dataset loading...")
    
    if not os.path.exists(POPULATION_DATASET_PATH):
        print("   ⚠ Population dataset not found, skipping")
        return
    
    df = load_population_dataset(POPULATION_DATASET_PATH)
    
    if len(df) > 0:
        assert "district" in df.columns, "Missing 'district' column"
        print(f"   ✓ Loaded {len(df)} population records")
    else:
        print("   ⚠ Population dataset loaded but empty")


def test_aggregation():
    """Test district-level aggregation."""
    print("\n[TEST] District aggregation...")
    df = pd.DataFrame({
        "district": ["Chennai", "Chennai", "Madurai"],
        "population": [1000000, 2000000, 1500000],
        "no_of_schools": [100, 50, 80],
        "literacy_rate": [85.0, 84.0, 75.0],
        "lat": [13.0, 13.1, 9.9],
        "lng": [80.0, 80.1, 78.1],
    })
    
    agg = aggregate_to_district_level(df)
    
    assert len(agg) == 2, f"Expected 2 districts, got {len(agg)}"
    
    # Check Chennai aggregation
    chennai = agg[agg["district"] == "Chennai"].iloc[0]
    assert chennai["population"] == 3000000, "Population not summed"
    assert chennai["no_of_schools"] == 150, "Schools not summed"
    assert abs(chennai["literacy_rate"] - 84.5) < 0.1, "Literacy rate not averaged"
    
    print("   ✓ Aggregated to district level: sum schools, avg literacy")


def test_merging():
    """Test dataset merging."""
    print("\n[TEST] Dataset merging...")
    school_df = pd.DataFrame({
        "district": ["Chennai", "Madurai"],
        "schools": [100, 50],
        "population": [5000000, 1500000],
    })
    
    pop_df = pd.DataFrame({
        "district": ["Chennai", "Madurai"],
        "population": [6000000, 1600000],
    })
    
    merged = merge_datasets(school_df, pop_df)
    
    assert len(merged) == 2, f"Expected 2 districts, got {len(merged)}"
    # Population from pop_df should be preferred
    assert merged[merged["district"] == "Chennai"]["population"].iloc[0] == 6000000
    
    print("   ✓ Datasets merged: population data integrated")


def test_feature_engineering():
    """Test feature engineering."""
    print("\n[TEST] Feature engineering...")
    df = pd.DataFrame({
        "district": ["Chennai", "Madurai"],
        "no_of_schools": [100, 50],
        "population": [5000000, 1500000],
        "literacy_rate": [85.0, 75.0],
        "dropout_rate": [5.0, 10.0],
        "rural_percentage": [25, 50],
    })
    
    features = engineer_features(df)
    
    assert "school_density" in features.columns, "Missing school_density"
    assert "literacy_factor" in features.columns, "Missing literacy_factor"
    assert "dropout_factor" in features.columns, "Missing dropout_factor"
    assert "urban_factor" in features.columns, "Missing urban_factor"
    
    # Check Chennai values
    chennai = features[features["district"] == "Chennai"].iloc[0]
    assert abs(chennai["dropout_factor"] - 95.0) < 0.1, "Dropout factor incorrect"
    assert abs(chennai["urban_factor"] - 75.0) < 0.1, "Urban factor incorrect"
    
    print("   ✓ Features engineered: density, literacy, dropout, urban")


def test_scoring():
    """Test scoring model."""
    print("\n[TEST] Scoring model...")
    df = pd.DataFrame({
        "district": ["Chennai", "Madurai"],
        "no_of_schools": [100, 50],
        "school_density": [0.00002, 0.00003],
        "literacy_factor": [85.0, 75.0],
        "dropout_factor": [95.0, 90.0],
        "urban_factor": [75.0, 50.0],
    })
    
    scored = score_districts(df)
    
    assert "score" in scored.columns, "Missing 'score' column"
    assert len(scored) == 2, f"Expected 2 rows, got {len(scored)}"
    
    # Scores should be in valid range
    for idx, row in scored.iterrows():
        assert 0 <= row["score"] <= 100, f"Score {row['score']} out of range"
    
    # Chennai should have higher score (more schools)
    assert scored[scored["district"] == "Chennai"]["score"].iloc[0] >= \
           scored[scored["district"] == "Madurai"]["score"].iloc[0]
    
    print(f"   ✓ Scoring applied: range 0-100")
    print(f"     Chennai score: {scored[scored['district'] == 'Chennai']['score'].iloc[0]:.0f}")
    print(f"     Madurai score: {scored[scored['district'] == 'Madurai']['score'].iloc[0]:.0f}")


def test_final_output():
    """Test final output formatting."""
    print("\n[TEST] Final output formatting...")
    df = pd.DataFrame({
        "district": ["chennai", "madurai"],
        "no_of_schools": [100, 50],
        "score": [85.0, 65.0],
        "lat": [13.0, 9.9],
        "lng": [80.0, 78.1],
    })
    
    final = prepare_final_output(df)
    
    assert set(final.columns) == {"district", "schools", "score", "lat", "lng"}
    assert final["district"].iloc[0] == "Chennai", "District not title-cased"
    assert final["schools"].dtype == int, "Schools not integer type"
    
    print("   ✓ Output formatted: correct columns, title case, proper types")


def test_caching():
    """Test result caching."""
    print("\n[TEST] Result caching...")
    df = pd.DataFrame({
        "district": ["Chennai", "Madurai"],
        "schools": [100, 50],
        "score": [85.0, 65.0],
        "lat": [13.0, 9.9],
        "lng": [80.0, 78.1],
    })
    
    cached = cache_results(df)
    
    assert isinstance(cached, list), "Cache should be a list"
    assert len(cached) == 2, f"Expected 2 items, got {len(cached)}"
    assert isinstance(cached[0], dict), "Cache items should be dicts"
    assert "district" in cached[0], "Missing district key"
    
    print(f"   ✓ Cached {len(cached)} districts as list of dicts")


def test_full_pipeline():
    """Test complete pipeline end-to-end."""
    print("\n[TEST] FULL PIPELINE TEST")
    print("=" * 70)
    
    if not os.path.exists(SCHOOL_DATASET_PATH):
        print("⚠ School dataset not found - cannot run full pipeline test")
        return
    
    try:
        cached, stats = run_data_pipeline(
            SCHOOL_DATASET_PATH,
            POPULATION_DATASET_PATH if os.path.exists(POPULATION_DATASET_PATH) else None,
            METADATA_DATASET_PATH if os.path.exists(METADATA_DATASET_PATH) else None,
        )
        
        print("\n[RESULTS]")
        print(f"   ✓ Districts: {stats['districts']}")
        print(f"   ✓ Score range: {stats['score_range'][0]:.0f} - {stats['score_range'][1]:.0f}")
        print(f"   ✓ Cached items: {len(cached)}")
        
        if cached:
            print(f"\n   Top 3 districts:")
            for i, d in enumerate(cached[:3], 1):
                print(f"     {i}. {d['district']}: {d['score']:.0f} | {d['schools']} schools")
        
        return True
    
    except Exception as e:
        print(f"\n   ✗ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PRODUCTION DATA PIPELINE - TEST SUITE")
    print("=" * 70)
    
    try:
        # Unit tests
        test_clean_columns()
        test_normalize_district()
        test_remove_duplicates()
        test_normalize_function()
        test_load_school_dataset()
        test_load_population_dataset()
        test_aggregation()
        test_merging()
        test_feature_engineering()
        test_scoring()
        test_final_output()
        test_caching()
        
        # Full pipeline test
        pipeline_ok = test_full_pipeline()
        
        print("\n" + "=" * 70)
        if pipeline_ok:
            print("✓ ALL TESTS PASSED")
        else:
            print("⚠ SOME TESTS FAILED - CHECK OUTPUT ABOVE")
        print("=" * 70 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
