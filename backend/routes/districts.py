import os
import numpy as np
import pandas as pd
from flask import Blueprint, jsonify
from utils.config import SCHOOL_DATASET_PATH
from utils.download_data import download_if_missing

districts_bp = Blueprint("districts", __name__)

# Primary data source - can be overridden by environment variable
CSV_PATH = os.getenv("DISTRICT_DATA_PATH") or os.path.join(
    os.path.dirname(__file__), "..", "data", "district_school_data.csv"
)

# ── alias map: any variant → single canonical lowercase name ──────────────────
DISTRICT_ALIAS = {
    "kanniyakumari": "kanyakumari",
    "kanyakumari":   "kanyakumari",
    "the nilgiris":  "nilgiris",
    "nilgiris":      "nilgiris",
    "tuticorin":     "thoothukudi",
    "thoothukudi":   "thoothukudi",
    "thiruvallur":   "tiruvallur",
    "tiruvallur":    "tiruvallur",
    "thiruvarur":    "tiruvarur",
    "tiruvarur":     "tiruvarur",
    "tirupathur":    "tirupattur",
    "tirupattur":    "tirupattur",
    "kancheepuram":  "kanchipuram",
    "kanchipuram":   "kanchipuram",
    "trichy":        "tiruchirappalli",
}

def _normalize(name: str) -> str:
    """Lowercase + strip + drop leading 'the '."""
    return str(name).lower().strip().removeprefix("the ").strip()

def _canonical(name: str) -> str:
    n = _normalize(name)
    return DISTRICT_ALIAS.get(n, n)

def load_data():
    """Load district data with error handling and fallback."""
    try:
        # 6. Ensure dataset loading supports external sources/automatic download
        if not os.path.exists(CSV_PATH):
            print(f"[DATA] Local data missing at {CSV_PATH}. Checking for base dataset...")
            # If the processed data is missing, we might need the base dataset
            download_if_missing(SCHOOL_DATASET_PATH)
            # In a real production app, we might trigger a pipeline run here 
            # or download the processed CSV directly from a CDN/Drive.
            
        if not os.path.exists(CSV_PATH):
            print(f"[ERROR] Data file not found: {CSV_PATH}")
            return []

        df = pd.read_csv(CSV_PATH)

        # ── normalise column names ────────────────────────────────────────────
        df.columns = df.columns.str.strip().str.lower()

        # rename 'lon' → 'lng' if needed
        if "lon" in df.columns and "lng" not in df.columns:
            df = df.rename(columns={"lon": "lng"})

        # ── canonical lowercase district names ────────────────────────────────
        if "district" in df.columns:
            df["district"] = df["district"].map(_canonical)

        # ── score calculation (if not already present) ────────────────────────
        if "score" not in df.columns and "schools" in df.columns:
            df["log_schools"] = np.log1p(df["schools"])
            max_log = df["log_schools"].max()
            min_log = df["log_schools"].min()
            if max_log != min_log:
                df["score"] = ((df["log_schools"] - min_log) / (max_log - min_log) * 100).round(2)
            else:
                df["score"] = 50.0

        # ── keep only needed columns ──────────────────────────────────────────
        cols = [c for c in ["district", "schools", "score", "lat", "lng"] if c in df.columns]
        df = df[cols]

        return df.to_dict(orient="records")

    except Exception as exc:
        # 7. Ensure the app does not crash if dataset is missing
        print(f"[ERROR] Failed to load district data: {exc}")
        return []

# Lazy loading to avoid issues with missing files during module import
_cached_data = None

def get_data():
    global _cached_data
    if _cached_data is None:
        _cached_data = load_data()
    return _cached_data

@districts_bp.route("/api/districts")
def get_districts():
    return jsonify(get_data())

@districts_bp.route("/api/summary")
def get_summary():
    data = get_data()
    if not data:
        return jsonify({
            "total_schools": 0, "total_districts": 0,
            "avg_score": 0, "high_priority": 0, "score_range": [0, 0]
        })

    scores = [d.get("score", 0) for d in data]
    return jsonify({
        "total_schools":   int(sum(d.get("schools", 0) for d in data)),
        "total_districts": len(data),
        "avg_score":       round(sum(scores) / len(scores), 2) if scores else 0,
        "high_priority":   sum(1 for s in scores if s >= 70),
        "score_range":     [round(min(scores), 2), round(max(scores), 2)] if scores else [0, 0],
    })

@districts_bp.route("/api/refresh", methods=["POST"])
def refresh_data():
    global _cached_data
    _cached_data = load_data()
    return jsonify({
        "status": "success",
        "message": f"Reloaded {len(_cached_data)} districts",
        "districts_count": len(_cached_data)
    })

@districts_bp.route("/api/health")
def health_check():
    data = get_data()
    return jsonify({
        "status": "healthy" if data else "degraded",
        "districts_loaded": len(data)
    })

