import pandas as pd
import numpy as np
import json
import os

from utils.download_data import ensure_dataset

# ---------- helpers ----------
DISTRICT_ALIAS = {
    "kanniyakumari": "kanyakumari",
    "the nilgiris": "nilgiris",
    "tuticorin": "thoothukudi",
    "trichy": "tiruchirappalli",
    "tiruvallur": "thiruvallur",
    "kancheepuram": "kanchipuram"
}

def normalize_name(x: str) -> str:
    if pd.isna(x):
        return ""
    name = str(x).lower().replace("the ", "").strip()
    return DISTRICT_ALIAS.get(name, name)

def minmax(s):
    if s.max() == s.min():
        return s * 0 + 0.5
    return (s - s.min()) / (s.max() - s.min())

# ---------- main pipeline ----------
def run_choropleth_pipeline():
    print("Running choropleth data pipeline...")

    # ---------- ensure dataset ----------
    if not download_if_missing(SCHOOL_DATASET_PATH):
        print("Warning: Dataset missing and download failed. Pipeline may fail.")

    DATA_PATH = SCHOOL_DATASET_PATH

    # ---------- load ----------
    try:
        df = pd.read_csv(DATA_PATH, low_memory=False)
    except FileNotFoundError:
        print(f"Error: Dataset not found at {DATA_PATH}")
        return

    df.columns = df.columns.str.lower().str.strip()

    if "district" not in df.columns:
        print("Error: 'district' column missing in dataset.")
        return

    df["district"] = df["district"].apply(normalize_name)

    # ---------- FIX: aggregate schools per district ----------
    df["schools"] = 1

    df = df.groupby("district").agg({
        "schools": "sum"
    }).reset_index()

    # ---------- dummy location ----------
    df["lat"] = 0
    df["lon"] = 0

    # ---------- population fallback ----------
    df["population"] = 100000

    # ---------- features ----------
    df["school_density"] = df["schools"] / (df["population"] + 1)
    df["log_schools"] = np.log1p(df["schools"])

    # ---------- normalize ----------
    df["schools_norm"] = minmax(df["log_schools"])
    df["density_norm"] = minmax(df["school_density"])

    # ---------- score ----------
    df["score"] = (
        0.6 * df["schools_norm"] +
        0.4 * df["density_norm"]
    ) * 100

    # ---------- clean output ----------
    out = df[["district", "schools", "population", "score", "lat", "lon"]].copy()
    out = out.rename(columns={"lon": "lng"})
    out = out.sort_values("score", ascending=False)

    out["score"] = out["score"].round(2)

    # ---------- save ----------
    output_path = "backend/data/district_scored.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(out.to_dict(orient="records"), f, indent=2)

    print(f"Saved → {output_path}")
    print(out.head())

# ---------- run ----------
if __name__ == "__main__":
    run_choropleth_pipeline()