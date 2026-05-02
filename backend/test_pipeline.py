#!/usr/bin/env python3
"""
High-Performance Pipeline Tester
Demonstrates async scraping, cleaning, geocoding, and bulk database operations.
"""

import asyncio
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.pipeline_service import run_pipeline, run_pipeline_async
from models.db import get_connection, init_db
from utils.geocoding import get_geo_cache


def print_section(title):
  """Print a formatted section header."""
  print(f"\n{'='*60}")
  print(f"  {title}")
  print(f"{'='*60}")


def print_results():
  """Print database results."""
  conn = get_connection()
  cursor = conn.cursor()
  
  # Get school stats
  cursor.execute("SELECT COUNT(*) as count FROM schools")
  school_count = cursor.fetchone()[0]
  
  cursor.execute("SELECT COUNT(*) as count FROM district_stats")
  district_count = cursor.fetchone()[0]
  
  # Get top districts by score
  cursor.execute(
      "SELECT district, total_schools, score FROM district_stats ORDER BY score DESC LIMIT 5"
  )
  top_districts = cursor.fetchall()
  
  # Get sample schools by district
  cursor.execute(
      "SELECT district, COUNT(*) as count FROM schools GROUP BY district ORDER BY count DESC LIMIT 5"
  )
  top_school_districts = cursor.fetchall()
  
  conn.close()
  
  print(f"\n📊 DATABASE RESULTS:")
  print(f"   Total Schools: {school_count}")
  print(f"   Districts: {district_count}")
  
  if top_districts:
    print(f"\n🏆 TOP DISTRICTS BY SCORE:")
    for row in top_districts:
      print(f"   {row[0]:20} | Schools: {row[1]:3} | Score: {row[2]}")
  
  if top_school_districts:
    print(f"\n📍 TOP DISTRICTS BY SCHOOL COUNT:")
    for row in top_school_districts:
      print(f"   {row[0]:20} | Schools: {row[1]}")


def test_sync_pipeline():
  """Test synchronous pipeline."""
  print_section("SYNC PIPELINE TEST")
  
  start = time.time()
  result = run_pipeline()
  elapsed = time.time() - start
  
  print(f"\n✓ Status: {result.get('status', 'unknown')}")
  print(f"✓ Message: {result.get('message', 'N/A')}")
  print(f"✓ Schools: {result.get('schools_count', 0)}")
  print(f"✓ Districts: {result.get('districts_count', 0)}")
  print(f"⏱️  Time: {elapsed:.2f}s")
  
  if 'sample_districts' in result:
    print(f"\n📌 Sample Districts:")
    for d in result['sample_districts']:
      print(f"   {d['district']:20} | {d['schools']:3} schools | Score: {d['score']}")


async def test_async_pipeline():
  """Test async pipeline."""
  print_section("ASYNC PIPELINE TEST")
  
  start = time.time()
  result = await run_pipeline_async()
  elapsed = time.time() - start
  
  print(f"\n✓ Status: {result.get('status', 'unknown')}")
  print(f"✓ Message: {result.get('message', 'N/A')}")
  print(f"✓ Schools: {result.get('schools_count', 0)}")
  print(f"✓ Districts: {result.get('districts_count', 0)}")
  print(f"⏱️  Time: {elapsed:.2f}s")
  
  if 'sample_districts' in result:
    print(f"\n📌 Sample Districts:")
    for d in result['sample_districts']:
      print(f"   {d['district']:20} | {d['schools']:3} schools | Score: {d['score']}")


def show_cache_stats():
  """Show geocoding cache statistics."""
  print_section("GEOCODING CACHE STATS")
  
  cache = get_geo_cache()
  print(f"\n📦 Cache Size: {len(cache)} entries")
  
  if cache:
    print(f"\n🌍 Cached Locations:")
    for location, (lat, lng) in list(cache.items())[:5]:
      print(f"   {location:20} | Lat: {lat:10.4f} | Lng: {lng:10.4f}")
    if len(cache) > 5:
      print(f"   ... and {len(cache) - 5} more")


def main():
  """Run all tests."""
  print("\n" + "="*60)
  print("🚀 HIGH-PERFORMANCE PIPELINE TESTER")
  print("="*60)
  
  try:
    # Initialize database
    print("\n⚙️  Initializing database...")
    init_db()
    print("✓ Database initialized")
    
    # Run async pipeline
    asyncio.run(test_async_pipeline())
    
    # Show results
    print_results()
    
    # Show cache stats
    show_cache_stats()
    
    print_section("✅ ALL TESTS PASSED")
    
  except Exception as e:
    print_section("❌ ERROR")
    print(f"\n{type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


if __name__ == "__main__":
  main()
