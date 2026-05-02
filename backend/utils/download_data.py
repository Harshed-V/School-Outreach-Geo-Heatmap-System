import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default File ID from Google Drive (can be overridden)
DEFAULT_FILE_ID = os.getenv("GOOGLE_DRIVE_FILE_ID", "1uKIsAeQE48LY5xg2d6ScqkxPcx0kO-FF")

def download_if_missing(path, file_id=None):
    """
    Downloads a dataset from Google Drive if it's missing locally.
    
    Args:
        path: Local destination path
        file_id: Google Drive file ID (defaults to DEFAULT_FILE_ID)
    
    Returns:
        bool: True if file exists or was downloaded successfully, False otherwise.
    """
    if os.path.exists(path):
        # Optional: check if file is empty
        if os.path.getsize(path) > 0:
            return True
        else:
            logger.warning(f"File at {path} is empty. Re-downloading...")

    target_file_id = file_id or DEFAULT_FILE_ID
    if not target_file_id:
        logger.error("No Google Drive File ID provided for download.")
        return False

    logger.info(f"Dataset missing at {path}. Starting download from Google Drive (ID: {target_file_id})...")
    
    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()
    
    try:
        # First request to get the confirmation token for large files
        response = session.get(URL, params={"id": target_file_id}, stream=True, timeout=30)
        
        token = None
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                token = value
                break

        # Second request with the token if needed
        if token:
            response = session.get(URL, params={"id": target_file_id, "confirm": token}, stream=True, timeout=30)
        else:
            # Fallback if no token (might be small file or direct download available)
            response = session.get(URL, params={"id": target_file_id}, stream=True, timeout=30)

        response.raise_for_status()

        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, "wb") as f:
            # Use streaming to avoid loading large files into memory
            downloaded = 0
            for chunk in response.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
            
        logger.info(f"Successfully downloaded {downloaded} bytes to {path}.")
        return True
    except Exception as e:
        logger.error(f"Download failed for {path}: {e}")
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
        return False