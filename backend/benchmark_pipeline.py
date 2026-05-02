#!/usr/bin/env python3
"""
Performance Benchmark Suite
Tests and measures performance of high-performance pipeline components.
"""

import asyncio
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scraper.school_scraper import scrape_schools_async, scrape_schools
from services.processing_service import process_school_data, process_school_data_async
from services.scoring_service import score_districts
from utils.geocoding import get_geo_cache, clear_geo_cache


def measure_time(func, name, *args, **kwargs):
  """Measure execution time of a function."""
  print(f"\n⏱️  {name}...", end=" ", flush=True)
  start = time.time()
  result = func(*args, **kwargs)
  elapsed = time.time() - start
  print(f"✓ {elapsed:.2f}s")
  return result, elapsed


async def measure_time_async(coro, name):
  """Measure execution time of async function."""
  print(f"\n⏱️  {name}...", end=" ", flush=True)
  start = time.time()
  result = await coro
  elapsed = time.time() - start
  print(f"✓ {elapsed:.2f}s")
  return result, elapsed


def benchmark_sync_pipeline():
  """Benchmark synchronous pipeline."""
  print("\n" + "="*60)
  print("📊 SYNCHRONOUS PIPELINE BENCHMARK")
  print("="*60)
  
  # Scraping
  raw, scrape_time = measure_time(scrape_schools, "Scraping (sync)")
  print(f"   Records: {len(raw)}")
  
  # Processing
  clean, process_time = measure_time(process_school_data, "Processing (sync)", raw)
  print(f"   Cleaned: {len(clean)}")
  
  # Scoring
  scores, score_time = measure_time(score_districts, "Scoring (sync)", clean)
  print(f"   Scored: {len(scores)}")
  
  total = scrape_time + process_time + score_time
  print(f"\n📈 SYNC TOTALS:")
  print(f"   Scrape:  {scrape_time:7.2f}s ({100*scrape_time/total:.1f}%)")
  print(f"   Process: {process_time:7.2f}s ({100*process_time/total:.1f}%)")
  print(f"   Score:   {score_time:7.2f}s ({100*score_time/total:.1f}%)")
  print(f"   TOTAL:   {total:7.2f}s")
  
  return {
    "scrape": scrape_time,
    "process": process_time,
    "score": score_time,
    "total": total,
    "records": len(raw),
    "schools": len(clean)
  }


async def benchmark_async_pipeline():
  """Benchmark asynchronous pipeline."""
  print("\n" + "="*60)
  print("🚀 ASYNCHRONOUS PIPELINE BENCHMARK")
  print("="*60)
  
  clear_geo_cache()
  
  # Scraping (async)
  raw, scrape_time = await measure_time_async(scrape_schools_async(), "Scraping (async)")
  print(f"   Records: {len(raw)}")
  
  # Processing (async)
  clean, process_time = await measure_time_async(
      process_school_data_async(raw),
      "Processing (async)"
  )
  print(f"   Cleaned: {len(clean)}")
  
  # Scoring
  scores, score_time = measure_time(score_districts, "Scoring (sync)", clean)
  print(f"   Scored: {len(scores)}")
  
  total = scrape_time + process_time + score_time
  print(f"\n📈 ASYNC TOTALS:")
  print(f"   Scrape:  {scrape_time:7.2f}s ({100*scrape_time/total:.1f}%)")
  print(f"   Process: {process_time:7.2f}s ({100*process_time/total:.1f}%)")
  print(f"   Score:   {score_time:7.2f}s ({100*score_time/total:.1f}%)")
  print(f"   TOTAL:   {total:7.2f}s")
  
  cache = get_geo_cache()
  print(f"\n📦 CACHE STATS:")
  print(f"   Cached: {len(cache)} locations")
  
  return {
    "scrape": scrape_time,
    "process": process_time,
    "score": score_time,
    "total": total,
    "records": len(raw),
    "schools": len(clean),
    "cache_hits": len(cache)
  }


async def benchmark_geocoding():
  """Benchmark geocoding with and without cache."""
  print("\n" + "="*60)
  print("🌍 GEOCODING PERFORMANCE")
  print("="*60)
  
  # Test 1: Cold cache
  clear_geo_cache()
  from utils.geocoding import geocode_address
  
  print(f"\n❄️  COLD CACHE (first run):")
  start = time.time()
  for i in range(3):
    geocode_address("School 1", "Chennai")
    print(f"   Request {i+1}/3...", end=" ", flush=True)
  cold_time = time.time() - start
  print(f"\n   Time: {cold_time:.2f}s ({cold_time/3:.2f}s per request)")
  
  # Test 2: Warm cache
  print(f"\n🔥 WARM CACHE (cached):")
  start = time.time()
  for i in range(10):
    geocode_address("School X", "Chennai")
  warm_time = time.time() - start
  print(f"   10 cached lookups: {warm_time:.4f}s ({1000*warm_time/10:.2f}ms per lookup)")
  
  speedup = cold_time / warm_time if warm_time > 0 else 0
  print(f"\n⚡ SPEEDUP: {speedup:.0f}× faster with cache")


def print_summary(sync_results, async_results):
  """Print comparison summary."""
  print("\n" + "="*60)
  print("📊 COMPARISON SUMMARY")
  print("="*60)
  
  sync_total = sync_results["total"]
  async_total = async_results["total"]
  improvement = ((sync_total - async_total) / sync_total) * 100
  speedup = sync_total / async_total if async_total > 0 else 0
  
  print(f"\n⏱️  TIMING:")
  print(f"   Sync:  {sync_total:7.2f}s")
  print(f"   Async: {async_total:7.2f}s")
  print(f"   ⚡ Speedup: {speedup:.2f}× ({improvement:.1f}% faster)")
  
  print(f"\n📈 DATA PROCESSED:")
  print(f"   Records: {async_results['records']}")
  print(f"   Schools: {async_results['schools']}")
  print(f"   Cache Hits: {async_results['cache_hits']}")
  
  # Throughput
  if async_total > 0:
    throughput = async_results['records'] / async_total
    print(f"\n🔄 THROUGHPUT:")
    print(f"   {throughput:.0f} records/second")


async def main():
  """Run all benchmarks."""
  print("\n" + "="*60)
  print("⚡ HIGH-PERFORMANCE PIPELINE BENCHMARKS")
  print("="*60)
  
  try:
    # Run sync benchmark
    sync_results = benchmark_sync_pipeline()
    
    # Run async benchmark
    async_results = await benchmark_async_pipeline()
    
    # Geocoding benchmark
    await benchmark_geocoding()
    
    # Summary
    print_summary(sync_results, async_results)
    
    print("\n" + "="*60)
    print("✅ BENCHMARKS COMPLETE")
    print("="*60 + "\n")
    
  except Exception as e:
    print(f"\n❌ Benchmark failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


if __name__ == "__main__":
  asyncio.run(main())
