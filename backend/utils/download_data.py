import os
import requests

FILE_ID = "1uKIsAeQE48LY5xg2d6ScqkxPcx0kO-FF"

def download_if_missing(path):
    """
    Downloads the dataset from Google Drive if it's missing locally.
    Handles large file confirmation tokens.
    """
    if os.path.exists(path):
        return True

    print(f"Dataset not found at {path}. Downloading from Google Drive...")
    
    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()
    
    # First request to get the confirmation token for large files
    response = session.get(URL, params={"id": FILE_ID}, stream=True)
    
    token = None
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            token = value
            break

    # Second request with the token if needed
    if token:
        response = session.get(URL, params={"id": FILE_ID, "confirm": token}, stream=True)
    else:
        # Fallback if no token (might be small file or direct download available)
        response = session.get(URL, params={"id": FILE_ID}, stream=True)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    try:
        with open(path, "wb") as f:
            # Use streaming to avoid loading 300MB+ into memory
            for chunk in response.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)
        print("Download complete.")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        if os.path.exists(path):
            os.remove(path)
        return False

# Optional: Alternative using gdown (requires 'pip install gdown')
# def download_with_gdown(path):
#     import gdown
#     os.makedirs(os.path.dirname(path), exist_ok=True)
#     gdown.download(id=FILE_ID, output=path, quiet=False)