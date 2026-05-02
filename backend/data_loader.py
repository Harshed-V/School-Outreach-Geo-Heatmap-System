from utils.config import SCHOOL_DATASET_PATH
from utils.download_data import download_if_missing

CSV_PATH = SCHOOL_DATASET_PATH

REQUIRED_COLUMNS = {
    "district",
    "population",
    "no_of_schools",
    "literacy_rate",
    "dropout_rate",
    "rural_percentage",
    "lat",
    "long",
}

FALLBACK_COORDS = {
    "Chennai": (13.0827, 80.2707),
    "Coimbatore": (11.0168, 76.9558),
    "Madurai": (9.9252, 78.1198),
    "Salem": (11.6643, 78.1460),
    "Tiruchirappalli": (10.7905, 78.7047),
}

data_cache = None


def _priority(score):
  return "high" if score >= 70 else "medium" if score >= 40 else "low"


def _district_id(name):
  return re.sub(r"[^a-z0-9]+", "-", str(name).strip().lower()).strip("-")


def _normalize_column_name(column):
  return str(column).strip().lower().replace(" ", "_")


def _fallback_data():
  print("[WARN] Returning fallback dummy district data")
  return [
      {
          "id": _district_id(district),
          "name": district.title(),
          "district": district.title(),
          "schools": 0,
          "score": 0,
          "lat": float(coords[0]),
          "lng": float(coords[1]),
          "priority": "low",
      }
      for district, coords in sorted(FALLBACK_COORDS.items())
  ]


def _load_csv():
  if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

  df = pd.read_csv(CSV_PATH)
  df.columns = [_normalize_column_name(column) for column in df.columns]

  missing = sorted(REQUIRED_COLUMNS - set(df.columns))
  if missing:
    raise ValueError(f"CSV missing required columns: {', '.join(missing)}")

  df = df[list(REQUIRED_COLUMNS)].copy()
  df["district"] = df["district"].fillna("").astype(str).str.strip()
  df = df[df["district"] != ""]

  numeric_columns = REQUIRED_COLUMNS - {"district"}
  for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

  df["population"] = df["population"].clip(lower=0)
  df["no_of_schools"] = df["no_of_schools"].clip(lower=0)
  df["literacy_rate"] = df["literacy_rate"].clip(lower=0, upper=100)
  df["dropout_rate"] = df["dropout_rate"].clip(lower=0, upper=100)
  df["rural_percentage"] = df["rural_percentage"].clip(lower=0, upper=100)

  return df


def _process_csv():
  df = _load_csv()
  if df.empty:
    raise ValueError("CSV contains no usable district rows")

  district_df = (
      df.groupby("district", as_index=False)
      .agg(
          population=("population", "sum"),
          schools=("no_of_schools", "sum"),
          literacy_rate=("literacy_rate", "mean"),
          dropout_rate=("dropout_rate", "mean"),
          rural_percentage=("rural_percentage", "mean"),
          lat=("lat", "mean"),
          lng=("long", "mean"),
      )
  )

  district_df["school_density"] = (
      district_df["schools"] / district_df["population"].replace(0, pd.NA)
  ).fillna(0)

  district_df["raw_score"] = (
      (district_df["schools"] * 0.25)
      + (district_df["school_density"] * 100000 * 0.20)
      + ((100 - district_df["dropout_rate"]) * 0.20)
      + (district_df["literacy_rate"] * 0.20)
      + ((100 - district_df["rural_percentage"]) * 0.15)
  )

  min_score = district_df["raw_score"].min()
  max_score = district_df["raw_score"].max()
  if max_score == min_score:
    district_df["score"] = 100
  else:
    district_df["score"] = (
        (district_df["raw_score"] - min_score) / (max_score - min_score) * 100
    )

  district_df = district_df.sort_values("score", ascending=False)

  processed_data = []
  for row in district_df.to_dict(orient="records"):
    score = int(round(row["score"]))
    district_name = str(row["district"]).strip().title()
    processed_data.append({
        "id": _district_id(district_name),
        "name": district_name,
        "district": district_name,
        "schools": int(round(row["schools"])),
        "score": score,
        "lat": round(float(row["lat"]), 6),
        "lng": round(float(row["lng"]), 6),
        "priority": _priority(score),
    })

  return processed_data


def load_and_process_data():
  """Load, clean, aggregate, score, normalize, and cache district CSV data."""
  global data_cache

  if data_cache is None:
    # Ensure file exists before trying to load it
    download_if_missing(CSV_PATH)
    
    try:
      data_cache = _process_csv()
      print(f"[OK] Loaded {len(data_cache)} districts from CSV")
    except Exception as e:
      print(f"[ERROR] Failed to load district CSV: {e}")
      data_cache = _fallback_data()

  return data_cache
