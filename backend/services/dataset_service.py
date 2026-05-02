import os

import pandas as pd

from utils.geocoding import DISTRICT_DEFAULT_COORDS


FIELD_ALIASES = {
    "school_name": [
        "school_name",
        "school name",
        "school",
        "schoolname",
        "institution_name",
        "institution name",
        "name",
    ],
    "district": [
        "district",
        "district_name",
        "district name",
        "revenue_district",
        "udise_district",
    ],
    "category": [
        "category",
        "school_category",
        "school category",
        "school_type",
        "type",
        "management_category",
    ],
    "student_count": [
        "student_count",
        "student count",
        "students",
        "total_students",
        "total students",
        "enrolment",
        "enrollment",
        "total_enrolment",
        "total enrollment",
    ],
    "recent_growth": [
        "recent_growth",
        "recent growth",
        "new_schools",
        "activity",
        "growth",
    ],
    "population": [
        "population",
        "district_population",
        "estimated_population",
    ],
    "urban_index": [
        "urban_index",
        "urban index",
        "urbanisation_index",
        "urbanization_index",
    ],
}


def _canonical_name(column):
  return str(column).strip().lower().replace("-", "_")


def _find_column(columns, aliases):
  canonical_columns = {_canonical_name(column): column for column in columns}
  for alias in aliases:
    key = _canonical_name(alias)
    if key in canonical_columns:
      return canonical_columns[key]
  return None


def _normalize_category(value):
  raw = str(value or "").strip().lower()
  if not raw:
    return "primary"
  if "higher" in raw and ("sec" in raw or "secondary" in raw):
    return "higher secondary"
  if "high" in raw or "secondary" in raw:
    return "high"
  if "primary" in raw or "elementary" in raw:
    return "primary"
  return raw


def _clean_student_count(series):
  return pd.to_numeric(series, errors="coerce").fillna(0).clip(lower=0).astype(int)


def load_school_dataset(csv_path):
  """
  Load and normalize a Tamil Nadu school CSV dataset.

  Expected source examples: UDISE/SSA school-level exports. Column names can vary;
  FIELD_ALIASES maps common variants to the internal schema.
  """
  if not csv_path or not os.path.exists(csv_path):
    raise FileNotFoundError(f"School dataset CSV not found: {csv_path}")

  source = pd.read_csv(csv_path)
  columns = list(source.columns)

  school_col = _find_column(columns, FIELD_ALIASES["school_name"])
  district_col = _find_column(columns, FIELD_ALIASES["district"])
  category_col = _find_column(columns, FIELD_ALIASES["category"])
  student_col = _find_column(columns, FIELD_ALIASES["student_count"])
  growth_col = _find_column(columns, FIELD_ALIASES["recent_growth"])
  population_col = _find_column(columns, FIELD_ALIASES["population"])
  urban_col = _find_column(columns, FIELD_ALIASES["urban_index"])

  missing = []
  if not school_col:
    missing.append("school_name")
  if not district_col:
    missing.append("district")
  if missing:
    raise ValueError(
        "Dataset is missing required columns: "
        + ", ".join(missing)
        + ". Supported aliases are defined in services/dataset_service.py."
    )

  clean = pd.DataFrame({
      "school_name": source[school_col].fillna("").astype(str).str.strip(),
      "district": source[district_col].fillna("").astype(str).str.strip().str.lower(),
      "category": (
          source[category_col].fillna("").map(_normalize_category)
          if category_col
          else "primary"
      ),
  })

  clean["student_count"] = (
      _clean_student_count(source[student_col])
      if student_col
      else 0
  )

  if growth_col:
    clean["recent_growth"] = pd.to_numeric(source[growth_col], errors="coerce").fillna(0).clip(lower=0)
  if population_col:
    clean["population"] = pd.to_numeric(source[population_col], errors="coerce").fillna(0).clip(lower=1)
  if urban_col:
    clean["urban_index"] = pd.to_numeric(source[urban_col], errors="coerce").fillna(0).clip(lower=0, upper=1)

  clean = clean[(clean["school_name"] != "") & (clean["district"] != "")]
  clean = clean.drop_duplicates(subset=["school_name", "district"], keep="first")

  clean["type"] = clean["category"]
  clean["lat"] = clean["district"].map(lambda district: DISTRICT_DEFAULT_COORDS.get(district, (12.9716, 77.5946))[0])
  clean["lng"] = clean["district"].map(lambda district: DISTRICT_DEFAULT_COORDS.get(district, (12.9716, 77.5946))[1])

  return clean.reset_index(drop=True)


def aggregate_by_district(clean_df):
  """Aggregate normalized school rows into district-level metrics."""
  if clean_df.empty:
    return []

  grouped = clean_df.groupby("district", dropna=False)
  rows = []
  for district, group in grouped:
    total_schools = int(len(group))
    higher_secondary = int(group["category"].eq("higher secondary").sum())
    total_students = int(group["student_count"].sum()) if "student_count" in group else 0

    rows.append({
        "district": str(district).title(),
        "total_schools": total_schools,
        "higher_secondary_schools": higher_secondary,
        "total_students": total_students,
        "hs_ratio": higher_secondary / max(total_schools, 1),
        "lat": float(group.iloc[0]["lat"]),
        "lng": float(group.iloc[0]["lng"]),
    })

  return rows
