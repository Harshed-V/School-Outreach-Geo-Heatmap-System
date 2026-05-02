import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Primary data paths
DATA_DIR = os.getenv("DATA_DIR") or os.path.join(BASE_DIR, "data")
DATABASE_PATH = os.getenv("DATABASE_PATH") or os.path.join(BASE_DIR, "school_outreach.db")

# Google Drive File IDs for production auto-download
# (These can be set in Render environment variables)
SCHOOL_DATASET_GID = os.getenv("SCHOOL_DATASET_GID", "1uKIsAeQE48LY5xg2d6ScqkxPcx0kO-FF")
PROCESSED_DATA_GID = os.getenv("PROCESSED_DATA_GID", "") # Optional: ID for processed CSV

# File paths
SCHOOL_DATASET_PATH = (
    os.getenv("SCHOOL_DATASET_PATH")
    or os.path.join(DATA_DIR, "schools.csv")
)

DISTRICT_DATA_PATH = (
    os.getenv("DISTRICT_DATA_PATH")
    or os.path.join(DATA_DIR, "district_school_data.csv")
)

# Optional datasets
POPULATION_DATASET_PATH = os.path.join(DATA_DIR, "_TN Population  - Sheet1.csv")
METADATA_DATASET_PATH = os.path.join(DATA_DIR, "2015_16_Districtwise.csv")

PORT = int(os.getenv("PORT", "5000"))


