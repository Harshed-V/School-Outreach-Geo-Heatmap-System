# High-Performance School Data Pipeline

## Overview

This pipeline provides a fast, scalable system for scraping, cleaning, geocoding, and storing school data with minimal API overhead.

## Architecture

### 1. **Async Scraper** (`scraper/school_scraper.py`)
- **Technology**: `httpx` (async) + `asyncio` + `BeautifulSoup`
- **Concurrency**: 5 concurrent requests (configurable via `CONCURRENCY_LIMIT`)
- **Retry Logic**: Exponential backoff (0.5s, 1s, 2s attempts)
- **Timeout**: 15 seconds per request
- **Deduplication**: Hash-based (MD5 of name + district)

**Key Features:**
```python
# Concurrent requests with semaphore control
semaphore = asyncio.Semaphore(5)
async with semaphore:
    response = await client.get(url, timeout=15)

# Exponential backoff on failure
backoff = 0.5 * (2 ** attempt)  # 0.5s, 1s, 2s...
await asyncio.sleep(backoff)
```

### 2. **Data Processing** (`services/processing_service.py`)
- **Cleaning**: Normalization, deduplication, validation
- **Batched Geocoding**: Groups by district to reduce API calls
- **Caching**: In-memory cache prevents redundant requests

**Optimization:**
- Instead of geocoding each school individually (n requests), we geocode unique districts only (1-n requests where n << schools)
- Default coordinates for known districts (instant lookup)

### 3. **Geocoding** (`utils/geocoding.py`)
- **API**: Nominatim (OpenStreetMap)
- **Caching**: Dictionary-based in-memory cache
- **Rate Limiting**: 1 request/second (respects Nominatim ToS)
- **Fallback**: District defaults + India center

**Cache Example:**
```python
cache = {
    "chennai": (13.0827, 80.2707),
    "coimbatore": (11.0168, 76.9558),
    ...
}
```

### 4. **Scoring** (`services/scoring_service.py`)
**Formula:**
```
score = (total_schools × 2) + (higher_secondary_count × 3)
```

- Government schools used as proxy for higher secondary
- Higher weight on quality schools (×3 multiplier)

### 5. **Database** (`models/db.py`)
- **SQLite** for simplicity and portability
- **Indexes** on district for query performance
- **Bulk Insert** using `executemany()` (50-100× faster than row-by-row)

**Tables:**
```sql
schools (
    id, name, district, lat, lng, type
)

district_stats (
    district, total_schools, higher_secondary_count, score, lat, lng
)
```

### 6. **Pipeline Orchestration** (`services/pipeline_service.py`)

```python
async def run_pipeline_async():
    # 1. Async scrape all URLs concurrently
    raw_rows = await scrape_schools_async()
    
    # 2. Clean data (dedup, normalize, validate)
    clean_df = await process_school_data_async(raw_rows)
    
    # 3. Compute district scores
    district_stats = score_districts(clean_df)
    
    # 4. Bulk insert into database
    _bulk_insert_schools(clean_df)
    _bulk_insert_district_stats(district_stats)
```

## Performance Characteristics

### Benchmarks (Approximate)
| Operation | Time | Notes |
|-----------|------|-------|
| **Scraping** | 2-5s | Depends on source responsiveness |
| **Cleaning** | <1s | Deduplication + normalization |
| **Geocoding** | 30-60s | Rate-limited to 1 req/sec |
| **Bulk Insert** | <1s | Using executemany() |
| **Total** | 40-70s | For 2-3 sources with 100+ schools |

### Optimization Techniques

1. **Async/Concurrent I/O**
   - Multiple URLs fetched in parallel
   - Non-blocking operations with asyncio

2. **Batched Geocoding**
   - Group by district → 1 API call per district
   - Cache results → zero calls for known districts
   - Default coords → instant fallback

3. **Bulk Database Operations**
   - `executemany()` instead of `execute()` in loop
   - 50-100× faster for large datasets

4. **Smart Deduplication**
   - Hash-based (MD5) for O(1) lookup
   - Applied at parse time (no cleanup phase)

## Usage

### Run Pipeline (Auto)
```bash
cd backend
python -m flask --app app run
# Visit: /api/pipeline/refresh
```

### Run Pipeline (Manual)
```python
from services.pipeline_service import run_pipeline

result = run_pipeline()
print(result)
# {
#   "status": "success",
#   "schools_count": 145,
#   "districts_count": 2,
#   ...
# }
```

### Test Pipeline
```bash
cd backend
python test_pipeline.py
```

## API Integration

### Flask Routes
```python
@districts_bp.route('/api/pipeline/refresh', methods=['POST'])
def refresh():
    result = refresh_pipeline()
    return jsonify(result)

@districts_bp.route('/api/districts', methods=['GET'])
def get_districts():
    # Returns all district stats with scores
```

## Configuration

**Concurrency Control** (`school_scraper.py`):
```python
CONCURRENCY_LIMIT = 5          # Requests in parallel
REQUEST_TIMEOUT = 15           # Seconds per request
MAX_RETRIES = 3                # Retry attempts
INITIAL_BACKOFF = 0.5          # Starting backoff (seconds)
```

**Rate Limiting** (`geocoding.py`):
```python
_rate_limit_delay = 1  # 1 second between Nominatim requests
```

## Adding Data Sources

Add URLs to `SOURCE_URLS` in `scraper/school_scraper.py`:

```python
SOURCE_URLS = [
    ("https://example.com/schools", "District1"),
    ("https://example.com/schools", "District2"),
    # Add more...
]
```

The scraper handles:
- Table extraction (CSS: `.school-card`, `.name`, `.district`, `.address`)
- List extraction (CSS: `#mw-content-text ul li`)
- Type inference (govt vs private)
- Automatic deduplication

## Performance Tips

1. **Batch Operations**
   - Use `executemany()` for inserts
   - Commit once after all data

2. **Cache Aggressively**
   - Geocoding results in memory
   - Reuse district coordinates

3. **Limit Concurrency**
   - Don't spawn 100 concurrent requests
   - Use semaphore for backpressure

4. **Monitor Rate Limits**
   - Nominatim: 1 req/sec recommended
   - Implement exponential backoff
   - Cache results heavily

5. **Index Database**
   - Add indexes on frequently queried columns
   - Example: `idx_schools_district`

## Troubleshooting

### "Too many requests" error
- Nominatim rate limit hit
- Reduce `CONCURRENCY_LIMIT` or increase `_rate_limit_delay`
- Geocoding cache should prevent most requests

### Empty results
- Check if source URLs are valid
- Verify CSS selectors match page structure
- Use browser dev tools to inspect HTML

### Slow performance
- Check if geocoding cache is working
- Monitor concurrent request count
- Profile with `asyncio.run(run_pipeline_async())` and time.time()

## Future Improvements

1. **Distributed Scraping**: Queue-based system for 100+ schools
2. **Incremental Updates**: Only update changed districts
3. **Parallel Geocoding**: Multiple Nominatim servers
4. **Data Validation**: Schema validation with Pydantic
5. **Monitoring**: Metrics on performance, cache hits, errors
