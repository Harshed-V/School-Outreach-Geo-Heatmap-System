import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATABASE_PATH = os.getenv("DATABASE_PATH") or os.path.join(BASE_DIR, "school_outreach.db")

# Primary school dataset (auto-downloaded if missing)
SCHOOL_DATASET_PATH = (
    os.getenv("SCHOOL_DATASET_PATH")
    or os.path.join(BASE_DIR, "data", "schools.csv")
)

# Population dataset (optional, enhances district-level population data)
POPULATION_DATASET_PATH = (
    os.getenv("POPULATION_DATASET_PATH")
    or os.path.join(BASE_DIR, "data", "_TN Population  - Sheet1.csv")
)

# District metadata (optional, provides additional district-level metrics)
METADATA_DATASET_PATH = (
    os.getenv("METADATA_DATASET_PATH")
    or os.path.join(BASE_DIR, "data", "2015_16_Districtwise.csv")
)

PORT = int(os.getenv("PORT", "5000"))

