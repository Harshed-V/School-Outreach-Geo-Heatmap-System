#!/usr/bin/env python3
"""
Simple script to quickly test if the backend API is working.
Just shows JSON responses from endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(path, method="GET"):
  """Test a single endpoint and print response."""
  url = f"{BASE_URL}{path}"
  try:
    if method == "GET":
      response = requests.get(url, timeout=5)
    else:
      response = requests.post(url, timeout=5)
    
    print(f"\n{'='*60}")
    print(f"{method} {path}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    return True
  except requests.exceptions.ConnectionError:
    print(f"\n❌ Cannot connect to {BASE_URL}")
    print("Make sure backend is running: python app.py")
    return False
  except Exception as e:
    print(f"\n❌ Error: {e}")
    return False

if __name__ == "__main__":
  print("\n🔍 QUICK API TEST\n")
  
  # Test endpoints
  test_endpoint("/api/health")
  test_endpoint("/api/districts")
  test_endpoint("/api/summary")
  test_endpoint("/api/debug/config")
  
  print(f"\n{'='*60}")
  print("Done!")
  print(f"{'='*60}\n")
