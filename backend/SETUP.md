# Setup & Installation Guide

## Requirements

- Python 3.9+
- pip or conda

## Installation

### 1. Create Virtual Environment
```bash
cd backend
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the backend directory:
```bash
DATABASE_PATH=school_outreach.db
PORT=5000
FLASK_ENV=development
```

## Running the System

### Option 1: Automatic Pipeline on Startup
Edit `backend/app.py`:
```python
def create_app():
  app = Flask(__name__)
  CORS(app)
  app.register_blueprint(districts_bp)
  init_db()
  run_pipeline()  # Uncomment this line
  return app
```

Then run:
```bash
python app.py
```

### Option 2: Manual Pipeline Trigger
```bash
python app.py
# Then in another terminal or via API:
curl -X POST http://localhost:5000/api/refresh
```

### Option 3: Test Pipeline Directly
```bash
python test_pipeline.py
```

### Option 4: Run Performance Benchmarks
```bash
python benchmark_pipeline.py
```

## API Endpoints

### Get All Districts
```bash
GET /api/districts
```
**Response:**
```json
[
  {
    "district": "Chennai",
    "lat": 13.0827,
    "lng": 80.2707,
    "schools": 45,
    "higher_secondary_count": 15,
    "score": 135,
    "priority": "high"
  }
]
```

### Get District Details
```bash
GET /api/districts/<district_name>
```
**Response:**
```json
{
  "district": "Chennai",
  "total_schools": 45,
  "higher_secondary_count": 15,
  "score": 135,
  "lat": 13.0827,
  "lng": 80.2707,
  "schools": [
    {
      "name": "School Name",
      "type": "govt",
      "lat": 13.0850,
      "lng": 80.2700
    }
  ]
}
```

### Get Summary Statistics
```bash
GET /api/summary
```
**Response:**
```json
{
  "total_schools": 200,
  "total_districts": 5,
  "avg_score": 110.5,
  "high_priority_districts": 2,
  "school_types": {
    "govt": 120,
    "private": 80
  }
}
```

### Refresh Pipeline
```bash
POST /api/refresh
```
**Response:**
```json
{
  "status": "success",
  "message": "Pipeline completed successfully",
  "schools_count": 200,
  "districts_count": 5,
  "sample_districts": [...]
}
```

### Health Check
```bash
GET /api/health
```

## Database

### Database File
- Location: `school_outreach.db` (in backend directory)
- Type: SQLite3
- Size: ~1-5 MB for 100+ schools

### Database Schema
```sql
CREATE TABLE schools (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  district TEXT NOT NULL,
  lat REAL NOT NULL,
  lng REAL NOT NULL,
  type TEXT NOT NULL
);
CREATE INDEX idx_schools_district ON schools(district);

CREATE TABLE district_stats (
  district TEXT PRIMARY KEY,
  total_schools INTEGER NOT NULL,
  higher_secondary_count INTEGER DEFAULT 0,
  score INTEGER NOT NULL,
  lat REAL NOT NULL,
  lng REAL NOT NULL
);
```

### Backup Database
```bash
# Copy the database file
cp school_outreach.db school_outreach.backup.db

# Or with timestamp
cp school_outreach.db "school_outreach.backup.$(date +%Y%m%d-%H%M%S).db"
```

### Query Database Directly
```bash
sqlite3 school_outreach.db
> SELECT * FROM district_stats;
> SELECT COUNT(*) FROM schools;
> .exit
```

## Performance Tips

1. **Increase Concurrency** (if sources are fast):
   Edit `backend/scraper/school_scraper.py`:
   ```python
   CONCURRENCY_LIMIT = 10  # Increase from 5
   ```

2. **Disable Rate Limiting** (if using private API):
   Edit `backend/utils/geocoding.py`:
   ```python
   _rate_limit_delay = 0.1  # Reduce from 1
   ```

3. **Monitor Cache Hits**:
   Most requests should use cached coordinates:
   ```python
   cache = get_geo_cache()
   print(f"Cache size: {len(cache)}")  # Should grow
   ```

4. **Use Bulk Operations**:
   Pipeline already uses `executemany()` for ~50× speedup

## Troubleshooting

### "Address already in use" on port 5000
```bash
# Change port in .env
PORT=5001
```

### SSL/Certificate errors
```bash
# Use without certificate verification (dev only)
import httpx
httpx.get(url, verify=False)
```

### Nominatim "Too many requests"
```python
# Reduce concurrency or increase delay
CONCURRENCY_LIMIT = 3
_rate_limit_delay = 2
```

### Database locked
```bash
# Delete the database and reinitialize
rm school_outreach.db
python -c "from models.db import init_db; init_db()"
```

## Frontend Integration

The backend provides JSON APIs consumed by the React frontend:

```javascript
// Get all districts
fetch('/api/districts')
  .then(r => r.json())
  .then(data => {
    // data = [
    //   { district: "Chennai", lat: ..., lng: ..., schools: ... }
    // ]
  })

// Refresh pipeline
fetch('/api/refresh', { method: 'POST' })
  .then(r => r.json())
  .then(result => console.log(result.message))
```

## Deployment

### Docker
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Render
Already configured in `render.yaml`:
```bash
# Deploy to Render
git push
```

### Local Production
```bash
# With gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With Waitress (Windows-friendly)
pip install waitress
waitress-serve --port=5000 app:app
```

## Next Steps

1. ✅ Pipeline is running and fast
2. 🔄 Add more data sources in `SOURCE_URLS`
3. 📊 Monitor performance with `benchmark_pipeline.py`
4. 🌐 Deploy to Render (see `render.yaml`)
5. 🎨 Connect frontend to API endpoints
