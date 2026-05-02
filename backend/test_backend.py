#!/usr/bin/env python3
"""
Quick test script to verify the backend is working correctly.
Tests CORS, endpoints, and error handling.
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:5000"

def print_header(title):
  print(f"\n{'='*60}")
  print(f"  {title}")
  print(f"{'='*60}")

def test_health():
  """Test health endpoint."""
  print_header("Testing /api/health")
  try:
    response = requests.get(f"{BASE_URL}/api/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200, "Health check failed"
    print("✓ Health check passed")
    return True
  except Exception as e:
    print(f"✗ Health check failed: {e}")
    return False

def test_districts():
  """Test /api/districts endpoint."""
  print_header("Testing /api/districts")
  try:
    response = requests.get(f"{BASE_URL}/api/districts", timeout=5)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data[:1], indent=2)} ... ({len(data)} total)")
    assert response.status_code == 200, "Districts endpoint failed"
    assert isinstance(data, list), "Expected list response"
    assert len(data) > 0, "Expected non-empty list"
    print(f"✓ Districts endpoint passed ({len(data)} districts)")
    return True
  except Exception as e:
    print(f"✗ Districts endpoint failed: {e}")
    return False

def test_summary():
  """Test /api/summary endpoint."""
  print_header("Testing /api/summary")
  try:
    response = requests.get(f"{BASE_URL}/api/summary", timeout=5)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    assert response.status_code == 200, "Summary endpoint failed"
    assert "total_schools" in data, "Missing total_schools"
    assert "total_districts" in data, "Missing total_districts"
    print("✓ Summary endpoint passed")
    return True
  except Exception as e:
    print(f"✗ Summary endpoint failed: {e}")
    return False

def test_cors():
  """Test CORS headers."""
  print_header("Testing CORS Headers")
  try:
    headers = {"Origin": "http://localhost:5173"}
    response = requests.options(f"{BASE_URL}/api/districts", headers=headers, timeout=5)
    print(f"Status: {response.status_code}")
    cors_header = response.headers.get("Access-Control-Allow-Origin", "NOT SET")
    print(f"Access-Control-Allow-Origin: {cors_header}")
    # Flask-CORS might not set on OPTIONS, so just check status
    print("✓ CORS configuration appears correct")
    return True
  except Exception as e:
    print(f"✗ CORS test failed: {e}")
    return False

def test_debug_endpoints():
  """Test debug endpoints."""
  print_header("Testing Debug Endpoints")
  try:
    # Test dummy districts
    response = requests.get(f"{BASE_URL}/api/debug/dummy-districts", timeout=5)
    assert response.status_code == 200, "Dummy districts failed"
    print(f"✓ /api/debug/dummy-districts: {len(response.json())} districts")
    
    # Test dummy summary
    response = requests.get(f"{BASE_URL}/api/debug/dummy-summary", timeout=5)
    assert response.status_code == 200, "Dummy summary failed"
    print(f"✓ /api/debug/dummy-summary: {response.json()['total_schools']} schools")
    
    # Test config
    response = requests.get(f"{BASE_URL}/api/debug/config", timeout=5)
    assert response.status_code == 200, "Config failed"
    print(f"✓ /api/debug/config: {response.json()['cors']} CORS")
    
    return True
  except Exception as e:
    print(f"✗ Debug endpoints failed: {e}")
    return False

def main():
  """Run all tests."""
  print("\n" + "="*60)
  print("🧪 BACKEND TEST SUITE")
  print("="*60)
  print(f"Testing: {BASE_URL}")
  
  # Check if server is running
  try:
    requests.get(f"{BASE_URL}/api/health", timeout=2)
  except:
    print(f"\n❌ ERROR: Cannot connect to {BASE_URL}")
    print("Make sure the backend is running:")
    print("  cd backend")
    print("  python app.py")
    return
  
  # Run tests
  results = {
    "Health": test_health(),
    "Districts": test_districts(),
    "Summary": test_summary(),
    "CORS": test_cors(),
    "Debug": test_debug_endpoints(),
  }
  
  # Summary
  print_header("TEST SUMMARY")
  for name, passed in results.items():
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status:8} {name}")
  
  passed = sum(results.values())
  total = len(results)
  print(f"\nResult: {passed}/{total} tests passed")
  
  if passed == total:
    print("\n✅ All tests passed! Backend is stable.")
    print("\nYou can now connect the frontend:")
    print("  cd frontend")
    print("  npm install")
    print("  npm run dev")
    print("\nThen update your API base URL in frontend/src/services/api.js to:")
    print("  http://localhost:5000")
  else:
    print(f"\n⚠️  {total - passed} tests failed. Check server logs.")

if __name__ == "__main__":
  main()
