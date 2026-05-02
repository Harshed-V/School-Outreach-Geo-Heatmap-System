import os
import logging
import numpy as np
import pandas as pd
from flask import Blueprint, jsonify
from utils.config import SCHOOL_DATASET_PATH, DISTRICT_DATA_PATH, SCHOOL_DATASET_GID
from utils.download_data import download_if_missing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

districts_bp = Blueprint("districts", __name__)

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
        # 3. Dataset handling (IMPORTANT)
        if not os.path.exists(DISTRICT_DATA_PATH):
            logger.warning(f"Processed data missing at {DISTRICT_DATA_PATH}. Checking base dataset...")
            
            # Try to ensure base dataset exists
            if download_if_missing(SCHOOL_DATASET_PATH, SCHOOL_DATASET_GID):
                logger.info("Base dataset verified/downloaded. You may need to run the pipeline to generate processed data.")
                # Note: We could trigger the pipeline here, but for production 
                # we prefer serving a fallback or existing processed file.
            else:
                logger.error("Base dataset could not be retrieved.")

        if not os.path.exists(DISTRICT_DATA_PATH):
            logger.error(f"Final data file not found: {DISTRICT_DATA_PATH}")
            return []

        logger.info(f"Loading district data from {DISTRICT_DATA_PATH}...")
        df = pd.read_csv(DISTRICT_DATA_PATH)

        # ── normalise column names ────────────────────────────────────────────
        df.columns = df.columns.str.strip().str.lower()

        # rename 'lon' → 'lng' if needed
        if "lon" in df.columns and "lng" not in df.columns:
            df = df.rename(columns={"lon": "lng"})

        # ── canonical lowercase district names ────────────────────────────────
        if "district" in df.columns:
            df["district"] = df["district"].map(_canonical)

        # ── score calculation (fallback) ────────────────────────
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

        data = df.to_dict(orient="records")
        logger.info(f"Successfully loaded {len(data)} districts.")
        return data

    except Exception as exc:
        # 7. Error handling - Ensure the app does not crash
        logger.error(f"Failed to load district data: {exc}", exc_info=True)
        return []

# Lazy loading
_cached_data = None

def get_data():
    global _cached_data
    if _cached_data is None:
        _cached_data = load_data()
    return _cached_data

@districts_bp.route("/api/districts")
def get_districts():
    data = get_data()
    if not data:
        return jsonify({"error": "Dataset unavailable", "message": "The server could not load school data"}), 503
    return jsonify(data)

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
        "dataset_loaded": bool(data),
        "districts_count": len(data)
    })


