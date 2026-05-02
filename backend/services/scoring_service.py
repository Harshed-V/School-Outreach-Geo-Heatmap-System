from collections import defaultdict
from math import sqrt


EPSILON = 1e-6

WEIGHTS = {
    "total_schools": 0.30,
    "hs_ratio": 0.20,
    "school_density": 0.15,
    "urban_index": 0.20,
    "recent_growth": 0.15,
}

# Census-style district population estimates. These are used only when the
# pipeline does not provide a population column.
DISTRICT_POPULATION_ESTIMATES = {
    "chennai": 7100000,
    "coimbatore": 3500000,
    "madurai": 3100000,
    "salem": 3500000,
    "trichy": 2700000,
    "tiruchirappalli": 2700000,
}

DISTRICT_URBAN_INDEX_ESTIMATES = {
    "chennai": 1.00,
    "coimbatore": 0.82,
    "madurai": 0.68,
    "salem": 0.52,
    "trichy": 0.62,
    "tiruchirappalli": 0.62,
}


def clamp(value, min_value=0.0, max_value=1.0):
  """Clamp a numeric value to a bounded range."""
  return max(min_value, min(max_value, float(value)))


def normalize(value, min_val, max_val):
  """Normalize a value to 0-1 using min-max scaling."""
  return clamp((float(value) - float(min_val)) / (float(max_val) - float(min_val) + EPSILON))


def _to_records(data):
  """Convert a pandas DataFrame or iterable of dicts into plain records."""
  if hasattr(data, "to_dict"):
    return data.to_dict("records")
  return list(data or [])


def _safe_float(value, default=0.0):
  try:
    if value is None:
      return default
    return float(value)
  except (TypeError, ValueError):
    return default


def _is_higher_secondary(record):
  if "higher_secondary" in record:
    return bool(record["higher_secondary"])
  if "is_higher_secondary" in record:
    return bool(record["is_higher_secondary"])
  school_type = str(record.get("type") or record.get("category") or "").strip().lower()
  return school_type in {"higher_secondary", "higher secondary", "hs", "govt"}


def _district_key(name):
  return str(name or "unknown").strip().lower()


def _district_label(name):
  return _district_key(name).title()


def _estimate_population(district_key, total_schools):
  if district_key in DISTRICT_POPULATION_ESTIMATES:
    return DISTRICT_POPULATION_ESTIMATES[district_key]
  # Conservative fallback: estimate from observed institution count.
  return max(100000, int(total_schools * 35000))


def _estimate_urban_index(district_key):
  return DISTRICT_URBAN_INDEX_ESTIMATES.get(district_key, 0.45)


def _estimate_growth(total_schools):
  # Smooth proxy when explicit recent_growth is missing. Larger active districts
  # get some growth credit without overwhelming the weighted model.
  return sqrt(max(total_schools, 0))


def _build_district_features(records):
  districts = defaultdict(lambda: {
      "total_schools": 0,
      "higher_secondary_schools": 0,
      "population_values": [],
      "urban_index_values": [],
      "recent_growth_values": [],
      "total_students": 0,
      "lat": None,
      "lng": None,
  })

  for record in records:
    district_key = _district_key(record.get("district"))
    district = districts[district_key]
    district["total_schools"] += 1

    if _is_higher_secondary(record):
      district["higher_secondary_schools"] += 1

    if "population" in record:
      district["population_values"].append(_safe_float(record.get("population")))
    if "urban_index" in record:
      district["urban_index_values"].append(clamp(_safe_float(record.get("urban_index"))))
    if "recent_growth" in record:
      district["recent_growth_values"].append(_safe_float(record.get("recent_growth")))
    if "student_count" in record:
      district["total_students"] += int(max(_safe_float(record.get("student_count")), 0))

    if district["lat"] is None:
      district["lat"] = _safe_float(record.get("lat"))
    if district["lng"] is None:
      district["lng"] = _safe_float(record.get("lng"))

  features = []
  for district_key, values in districts.items():
    total_schools = values["total_schools"]
    higher_secondary_schools = values["higher_secondary_schools"]
    population = (
        max(values["population_values"])
        if values["population_values"]
        else _estimate_population(district_key, total_schools)
    )
    urban_index = (
        sum(values["urban_index_values"]) / len(values["urban_index_values"])
        if values["urban_index_values"]
        else _estimate_urban_index(district_key)
    )
    recent_growth = (
        sum(values["recent_growth_values"])
        if values["recent_growth_values"]
        else _estimate_growth(total_schools)
    )

    features.append({
        "district": _district_label(district_key),
        "total_schools": total_schools,
        "higher_secondary_count": higher_secondary_schools,
        "population": max(population, 1.0),
        "urban_index": clamp(urban_index),
        "recent_growth": max(recent_growth, 0.0),
        "total_students": values["total_students"],
        "school_density": total_schools / max(population, 1.0),
        "hs_ratio": higher_secondary_schools / max(total_schools, 1),
        "lat": values["lat"] or 0.0,
        "lng": values["lng"] or 0.0,
    })

  return features


def score_districts(data):
  """
  Compute a 0-100 Outreach Potential Score per district.

  Model:
    0.30 * normalized total schools
    0.20 * normalized higher-secondary ratio
    0.15 * normalized school density
    0.20 * urban index
    0.15 * normalized recent growth
  """
  records = _to_records(data)
  if not records:
    return []

  features = _build_district_features(records)
  ranges = {
      "total_schools": (
          min(item["total_schools"] for item in features),
          max(item["total_schools"] for item in features),
      ),
      "hs_ratio": (
          min(item["hs_ratio"] for item in features),
          max(item["hs_ratio"] for item in features),
      ),
      "school_density": (
          min(item["school_density"] for item in features),
          max(item["school_density"] for item in features),
      ),
      "recent_growth": (
          min(item["recent_growth"] for item in features),
          max(item["recent_growth"] for item in features),
      ),
  }

  scored = []
  for item in features:
    norm_total_schools = normalize(item["total_schools"], *ranges["total_schools"])
    norm_hs_ratio = normalize(item["hs_ratio"], *ranges["hs_ratio"])
    norm_school_density = normalize(item["school_density"], *ranges["school_density"])
    norm_growth = normalize(item["recent_growth"], *ranges["recent_growth"])

    score_raw = (
        WEIGHTS["total_schools"] * norm_total_schools
        + WEIGHTS["hs_ratio"] * norm_hs_ratio
        + WEIGHTS["school_density"] * norm_school_density
        + WEIGHTS["urban_index"] * item["urban_index"]
        + WEIGHTS["recent_growth"] * norm_growth
    )

    scored.append({
        "district": item["district"],
        "total_schools": item["total_schools"],
        "higher_secondary_count": item["higher_secondary_count"],
        "total_students": item["total_students"],
        "score": int(clamp(score_raw) * 100),
        "lat": item["lat"],
        "lng": item["lng"],
    })

  return sorted(scored, key=lambda row: row["score"], reverse=True)
