# School Outreach Geo-Heatmap System

A robust, data-driven web application to visualize school outreach potential across Tamil Nadu districts using an interactive choropleth map.

## Features
- **Dynamic Choropleth Map**: District-level visualization using React-Leaflet and native GeoJSON.
- **Robust Data Pipeline**: Flask/Pandas backend that cleans and auto-normalizes data scoring (0-100 scale).
- **Hybrid Matching**: Merges a deterministic alias mapping with `Fuse.js` for bulletproof district resolution.
- **Missing Data Coverage**: Dynamically handles regions with no data with a clean gray placeholder to preserve map integrity.

## Tech Stack
- **Frontend**: React, Vite, Leaflet (`react-leaflet`), `Fuse.js`
- **Backend**: Python, Flask, Pandas

## Setup & Running

**Backend:**
```bash
cd backend
python -m venv .venv
# activate venv
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Your browser will automatically open and render the application!
