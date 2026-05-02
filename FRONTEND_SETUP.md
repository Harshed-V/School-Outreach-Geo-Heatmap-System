# Frontend Configuration Guide

## Setup for Frontend to Connect to Backend

### 1. Backend Running
First, ensure backend is running:
```bash
cd backend
pip install -r requirements.txt
python app.py
```

You should see:
```
============================================================
🚀 Starting School Outreach Geo-Heatmap Backend
============================================================
API Server: http://0.0.0.0:5000
Frontend: http://localhost:5173
CORS: Enabled for all origins (development mode)
============================================================
```

### 2. Test Backend API
```bash
# In a new terminal, from backend directory
python quick_test.py
```

You should see JSON responses from all endpoints without errors.

### 3. Configure Frontend API Client

Edit `frontend/src/services/api.js`:

```javascript
// ✓ CORRECT for local development
const API_BASE_URL = "http://localhost:5000";

// Usage:
const response = await fetch(`${API_BASE_URL}/api/districts`);
const data = await response.json();
```

### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 5. Check CORS is Working

If you see CORS errors in browser console:
```
Access to XMLHttpRequest at 'http://localhost:5000/api/districts' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution**: Backend CORS is already enabled. If error persists:
1. Hard refresh browser (Ctrl+Shift+R)
2. Clear browser cache
3. Restart backend: `python app.py`
4. Check `/api/debug/config` in browser

### 6. API Endpoints Available

#### Health Check
```bash
curl http://localhost:5000/api/health
```
Response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

#### All Districts
```bash
curl http://localhost:5000/api/districts
```
Response (with fallback dummy data if DB empty):
```json
[
  {
    "district": "Chennai",
    "lat": 13.0827,
    "lng": 80.2707,
    "schools": 120,
    "higher_secondary_count": 40,
    "score": 360,
    "priority": "high"
  },
  ...
]
```

#### Summary Statistics
```bash
curl http://localhost:5000/api/summary
```
Response:
```json
{
  "total_schools": 355,
  "total_districts": 5,
  "avg_score": 205.0,
  "high_priority_districts": 1,
  "school_types": {
    "govt": 185,
    "private": 170
  }
}
```

#### District Details
```bash
curl http://localhost:5000/api/districts/Chennai
```

#### Refresh Pipeline
```bash
curl -X POST http://localhost:5000/api/refresh
```

### 7. Debug Endpoints (Development Only)

These endpoints return dummy data for testing:

```bash
# Get dummy districts
curl http://localhost:5000/api/debug/dummy-districts

# Get dummy summary
curl http://localhost:5000/api/debug/dummy-summary

# Get config info
curl http://localhost:5000/api/debug/config
```

### 8. Error Handling

Backend will **never crash**. If something fails:
- Database error → Returns fallback dummy data
- Missing endpoint → Returns 404 JSON error
- Server error → Returns 500 JSON error with message

Example error response:
```json
{
  "error": "Internal Server Error",
  "message": "database is locked",
  "type": "OperationalError"
}
```

### 9. Frontend API Integration

In your React components:

```javascript
import { useEffect, useState } from 'react';

export function DistrictMap() {
  const [districts, setDistricts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch districts from backend
    fetch('http://localhost:5000/api/districts')
      .then(res => res.json())
      .then(data => {
        setDistricts(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load districts:', err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {districts.map(d => (
        <div key={d.district}>
          <h3>{d.district}</h3>
          <p>Schools: {d.schools}, Score: {d.score}</p>
        </div>
      ))}
    </div>
  );
}
```

### 10. Troubleshooting

#### "Cannot connect to http://localhost:5000"
```bash
# Make sure backend is running
cd backend
python app.py

# If port 5000 is in use, change it
# Edit backend/.env:
PORT=5001

# Then update frontend to use new port
```

#### CORS errors in console
```bash
# Usually fixes it:
1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Restart backend

# If still failing, check if CORS is enabled:
curl http://localhost:5000/api/debug/config
```

#### No data displayed (shows dummy data)
```bash
# Backend returns fallback dummy data if database is empty
# This is normal! To load real data:

# Option 1: Run the pipeline
curl -X POST http://localhost:5000/api/refresh

# Option 2: Check database directly
sqlite3 backend/school_outreach.db "SELECT COUNT(*) FROM district_stats;"
```

#### Backend crashes or freezes
```bash
# Check the console output for error messages
# Common issues:
# 1. Database locked - delete: rm backend/school_outreach.db
# 2. Port in use - change PORT in .env
# 3. Missing dependencies - pip install -r requirements.txt

# Restart with clean state:
cd backend
rm school_outreach.db  # Optional: reset database
python app.py
```

### 11. Production Deployment

For production (e.g., Vercel + Render):

**Frontend (.env.production)**:
```
VITE_API_BASE_URL=https://your-backend.render.com
```

**Backend (.env.production)**:
```
FLASK_ENV=production
DEBUG=false
CORS_ORIGINS=https://your-frontend.vercel.app
```

Update Flask CORS configuration:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-frontend.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
```

---

## Quick Checklist

- [ ] Backend running: `python app.py`
- [ ] Backend tests pass: `python quick_test.py`
- [ ] Frontend API URL set: `http://localhost:5000`
- [ ] Frontend running: `npm run dev`
- [ ] No CORS errors in console
- [ ] Data displaying on map
- [ ] Health check endpoint works: `http://localhost:5000/api/health`

---

If everything is working, you're ready to integrate the scraping pipeline!
