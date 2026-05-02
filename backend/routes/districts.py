"""
Districts API — loads district_school_data.csv directly.

Output contract (all lowercase district names, always):
  district  : str   canonical lowercase name (e.g. "kanyakumari", NOT "Kanyakumari")
  schools   : int
  score     : float  0–100, linear normalisation on school count
  lat       : float
  lng       : float  (note: CSV column is 'lon' — renamed here)
"""
import os
import numpy as np
import pandas as pd
from flask import Blueprint, jsonify

districts_bp = Blueprint("districts", __name__)

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "district_school_data.csv")

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
    "tirupathur":    "tirupattur",   # GeoJSON spells it Tirupathur
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
    try:
        df = pd.read_csv(CSV_PATH)

        # ── normalise column names ────────────────────────────────────────────
        df.columns = df.columns.str.strip().str.lower()

        # rename 'lon' → 'lng' if needed
        if "lon" in df.columns and "lng" not in df.columns:
            df = df.rename(columns={"lon": "lng"})

        # ── canonical lowercase district names (NO .title()) ─────────────────
        df["district"] = df["district"].map(_canonical)

        # ── score: log-normalised for smoother distribution ───────────────────
        df["log_schools"] = np.log1p(df["schools"])
        df["score"] = (
            (df["log_schools"] - df["log_schools"].min())
            / (df["log_schools"].max() - df["log_schools"].min())
            * 100
        ).round(2)

        # ── keep only needed columns ──────────────────────────────────────────
        cols = [c for c in ["district", "schools", "score", "lat", "lng"] if c in df.columns]
        df = df[cols]

        records = df.to_dict(orient="records")
        print(f"[API] Loaded {len(records)} districts from {CSV_PATH}")
        for r in records:
            print(f"  {r['district']:25s}  score={r['score']:.1f}  schools={r['schools']}")
        return records

    except Exception as exc:
        print(f"[ERROR] Failed to load district data: {exc}")
        return []


# Loaded once at startup
_data = load_data()


@districts_bp.route("/api/districts")
def get_districts():
    return jsonify(_data)


@districts_bp.route("/api/summary")
def get_summary():
    if not _data:
        return jsonify({"total_schools": 0, "total_districts": 0,
                        "avg_score": 0, "high_priority": 0, "score_range": [0, 0]})

    scores = [d["score"] for d in _data]
    return jsonify({
        "total_schools":   int(sum(d["schools"] for d in _data)),
        "total_districts": len(_data),
        "avg_score":       round(sum(scores) / len(scores), 2),
        "high_priority":   sum(1 for s in scores if s >= 70),
        "score_range":     [round(min(scores), 2), round(max(scores), 2)],
    })


@districts_bp.route("/api/refresh", methods=["POST"])
def refresh_data():
    """Reload data from CSV — called by the frontend Refresh button."""
    global _data
    _data = load_data()
    scores = [d["score"] for d in _data]
    return jsonify({
        "status": "success",
        "message": f"Reloaded {len(_data)} districts from CSV",
        "districts_count": len(_data),
        "score_range": [round(min(scores), 2), round(max(scores), 2)] if scores else [0, 0],
    })


@districts_bp.route("/api/health")
def health_check():
    return jsonify({"status": "healthy", "districts_loaded": len(_data)})
