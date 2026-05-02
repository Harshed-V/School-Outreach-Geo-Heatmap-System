import asyncio
import hashlib
from typing import Dict, List
from collections.abc import Callable

import httpx
from bs4 import BeautifulSoup


SOURCE_URLS = [
    ("https://en.wikipedia.org/wiki/List_of_schools_in_Chennai", "Chennai"),
    ("https://en.wikipedia.org/wiki/Education_in_Coimbatore", "Coimbatore"),
]

# Concurrency control
CONCURRENCY_LIMIT = 5
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
INITIAL_BACKOFF = 0.5  # seconds

HEADERS = {"User-Agent": "school-outreach-heatmap/1.0"}

# Global semaphore for concurrency control
_semaphore: asyncio.Semaphore | None = None


def _get_semaphore() -> asyncio.Semaphore:
  """Get or create the global semaphore."""
  global _semaphore
  if _semaphore is None:
    _semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
  return _semaphore


async def fetch_with_retry(
    client: httpx.AsyncClient,
    url: str,
    max_retries: int = MAX_RETRIES
) -> str | None:
  """Fetch URL with exponential backoff retry logic."""
  semaphore = _get_semaphore()
  
  for attempt in range(max_retries):
    async with semaphore:
      try:
        response = await client.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers=HEADERS
        )
        response.raise_for_status()
        return response.text
      except httpx.HTTPError as e:
        if attempt == max_retries - 1:
          print(f"Failed to fetch {url} after {max_retries} retries: {e}")
          return None
        backoff = INITIAL_BACKOFF * (2 ** attempt)
        await asyncio.sleep(backoff)
      except Exception as e:
        print(f"Unexpected error fetching {url}: {e}")
        return None
  
  return None


async def scrape_schools_async() -> List[Dict]:
  """Async scraper using httpx with concurrent requests."""
  async with httpx.AsyncClient() as client:
    tasks = [
        fetch_with_retry(client, url)
        for url, _ in SOURCE_URLS
    ]
    html_contents = await asyncio.gather(*tasks)
  
  schools = []
  for html, (_, district) in zip(html_contents, SOURCE_URLS):
    if html:
      schools.extend(_extract_schools_from_page(html, district))
  
  return schools


def scrape_schools() -> List[Dict]:
  """Synchronous wrapper for backward compatibility."""
  try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
      # If loop is already running, run in thread pool
      import concurrent.futures
      with concurrent.futures.ThreadPoolExecutor() as executor:
        return executor.submit(
            asyncio.run,
            scrape_schools_async()
        ).result()
    else:
      return asyncio.run(scrape_schools_async())
  except RuntimeError:
    return asyncio.run(scrape_schools_async())


def _extract_schools_from_page(html: str, district: str) -> List[Dict]:
  """Parse HTML and extract school data with deduplication."""
  extracted: List[Dict] = []
  seen_hashes = set()
  soup = BeautifulSoup(html, "html.parser")

  # Extract from tables
  for row in soup.select("table.wikitable tr"):
    cols = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
    if not cols:
      continue
    
    school_name = cols[0].strip()
    if school_name.lower() in {"name", "school", "institution"}:
      continue
    
    address = cols[1] if len(cols) > 1 else f"{district}, Tamil Nadu"
    school_type = _infer_type(" ".join(cols))
    
    entry = {
        "school_name": school_name,
        "district": district,
        "address": address.strip(),
        "type": school_type,
    }
    
    # Deduplicate by hash
    entry_hash = hashlib.md5(
        (entry["school_name"] + entry["district"]).encode()
    ).hexdigest()
    if entry_hash not in seen_hashes:
      seen_hashes.add(entry_hash)
      extracted.append(entry)

  # Extract from lists
  for item in soup.select("#mw-content-text ul li"):
    text = item.get_text(" ", strip=True)
    if not text or len(text) < 5:
      continue
    
    if "school" not in text.lower() and "academy" not in text.lower():
      continue
    
    school_name = text.split(" - ")[0][:120].strip()
    entry = {
        "school_name": school_name,
        "district": district,
        "address": f"{district}, Tamil Nadu",
        "type": _infer_type(text),
    }
    
    entry_hash = hashlib.md5(
        (entry["school_name"] + entry["district"]).encode()
    ).hexdigest()
    if entry_hash not in seen_hashes:
      seen_hashes.add(entry_hash)
      extracted.append(entry)

  return extracted


def _infer_type(text: str) -> str:
  """Infer school type from text."""
  lower = text.lower()
  if "government" in lower or "govt" in lower or "public" in lower:
    return "govt"
  return "private"
