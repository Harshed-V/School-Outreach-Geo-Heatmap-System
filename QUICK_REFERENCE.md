# Quick Reference Card

## Common Commands

### Initialize & Run
```bash
# Setup
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run API
python app.py

# Trigger pipeline via API
curl -X POST http://localhost:5000/api/refresh

# Get all districts
curl http://localhost:5000/api/districts
```

### Testing & Benchmarking
```bash
# Test pipeline
python test_pipeline.py

# Benchmark performance (sync vs async)
python benchmark_pipeline.py

# Direct database query
sqlite3 school_outreach.db "SELECT * FROM district_stats ORDER BY score DESC;"
```

## Configuration

### `.env` File
```bash
DATABASE_PATH=school_outreach.db
PORT=5000
RUN_PIPELINE_ON_STARTUP=false
FLASK_ENV=development
```

### Adjust Concurrency
Edit `backend/scraper/school_scraper.py`:
```python
CONCURRENCY_LIMIT = 5      # Default: 5 concurrent requests
REQUEST_TIMEOUT = 15       # Default: 15 seconds
MAX_RETRIES = 3            # Default: 3 retry attempts
```

### Adjust Rate Limiting
Edit `backend/utils/geocoding.py`:
```python
_rate_limit_delay = 1      # Default: 1 second between requests
```

### Add Data Sources
Edit `backend/scraper/school_scraper.py`:
```python
SOURCE_URLS = [
    ("https://source1.com/schools", "District1"),
    ("https://source2.com/schools", "District2"),
]
```

## API Endpoints

### Districts
```bash
# Get all districts (sorted by score)
GET /api/districts

# Get specific district details
GET /api/districts/{district_name}
```

### Statistics
```bash
# Get summary statistics
GET /api/summary

# Get health status
GET /api/health
```

### Pipeline
```bash
# Trigger pipeline refresh
POST /api/refresh
```

## Performance Tips

1. **Increase Speed**: Raise `CONCURRENCY_LIMIT` (but respect target server)
2. **Fix Rate Limits**: Lower `CONCURRENCY_LIMIT` or raise `_rate_limit_delay`
3. **Monitor Cache**: `from utils.geocoding import get_geo_cache; print(len(get_geo_cache()))`
4. **Clear Cache**: `from utils.geocoding import clear_geo_cache; clear_geo_cache()`

## Troubleshooting

### Port Already in Use
```bash
# Change in .env
PORT=5001
```

### Database Locked
```bash
# Delete and reinit
rm school_outreach.db
python -c "from models.db import init_db; init_db()"
```

### Too Many Geocoding Requests
```python
# In utils/geocoding.py
CONCURRENCY_LIMIT = 2
_rate_limit_delay = 2
```

### Check Pipeline Status
```python
from services.pipeline_service import run_pipeline
result = run_pipeline()
print(f"Status: {result['status']}")
print(f"Schools: {result['schools_count']}")
print(f"Districts: {result['districts_count']}")
```

## Database Queries

### View All Districts
```sql
SELECT * FROM district_stats ORDER BY score DESC;
```

### Count Schools by Type
```sql
SELECT type, COUNT(*) as count FROM schools GROUP BY type;
```

### Find Schools in District
```sql
SELECT name, type FROM schools WHERE district = 'Chennai' ORDER BY name;
```

### Get Cache Status
```sql
SELECT COUNT(DISTINCT district) as unique_districts FROM schools;
```

## File Structure Summary

```
backend/
├── app.py                 # Main Flask app
├── requirements.txt       # Dependencies
├── test_pipeline.py       # Test script
├── benchmark_pipeline.py  # Benchmark script
├── models/db.py           # Database schema
├── scraper/school_scraper.py    # Async scraper
├── services/
│   ├── pipeline_service.py      # Orchestration
│   ├── processing_service.py    # Data cleaning
│   └── scoring_service.py       # Scoring
├── utils/
│   ├── config.py                # Config
│   └── geocoding.py             # Geocoding + cache
└── routes/districts.py          # API routes
```

## Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| Scraping | <10s | 2-5s ✓ |
| Cleaning | <5s | <1s ✓ |
| Geocoding (cold) | <60s | 30-60s ✓ |
| Geocoding (warm) | <5s | <1s ✓ |
| Total (cold) | <70s | 40-70s ✓ |
| Total (warm) | <10s | <10s ✓ |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `school_outreach.db` | SQLite database file |
| `PORT` | `5000` | Flask server port |
| `RUN_PIPELINE_ON_STARTUP` | `false` | Run pipeline on app start |
| `FLASK_ENV` | `development` | Flask environment |

## Python Version
- Minimum: Python 3.9
- Recommended: Python 3.11+

## Dependencies Summary
- `Flask` - Web framework
- `httpx` - Async HTTP client
- `BeautifulSoup4` - HTML parsing
- `pandas` - Data processing
- `requests` - Sync HTTP (geocoding)

---

**Pro Tip**: Use `python test_pipeline.py` to validate everything works before deploying!
