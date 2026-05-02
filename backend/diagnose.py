#!/usr/bin/env python3
"""
Backend debugging script.
Checks dependencies, database, and configuration.
"""

import sys
import os

def check_python_version():
  """Check Python version."""
  print("🐍 Python Version")
  version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
  print(f"   {version}")
  if sys.version_info < (3, 9):
    print("   ⚠️  Minimum Python 3.9 required")
    return False
  print("   ✓")
  return True

def check_dependencies():
  """Check required dependencies."""
  print("\n📦 Dependencies")
  required = {
    "flask": "Flask",
    "flask_cors": "Flask-CORS",
    "httpx": "httpx",
    "bs4": "BeautifulSoup4",
    "pandas": "pandas",
    "dotenv": "python-dotenv",
  }
  
  all_ok = True
  for import_name, package_name in required.items():
    try:
      __import__(import_name)
      print(f"   ✓ {package_name}")
    except ImportError:
      print(f"   ✗ {package_name} - MISSING")
      all_ok = False
  
  if not all_ok:
    print("\n   Install missing dependencies:")
    print("   pip install -r requirements.txt")
  
  return all_ok

def check_database():
  """Check database configuration."""
  print("\n💾 Database")
  try:
    from models.db import get_connection, init_db
    
    # Initialize DB
    init_db()
    print("   ✓ Database initialized")
    
    # Connect and query
    conn = get_connection()
    conn.execute("SELECT 1")
    conn.close()
    print("   ✓ Database connection works")
    
    # Check tables
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_names = [t[0] for t in tables]
    
    if "district_stats" in table_names:
      print("   ✓ district_stats table exists")
    else:
      print("   ⚠️  district_stats table missing")
    
    if "schools" in table_names:
      print("   ✓ schools table exists")
    else:
      print("   ⚠️  schools table missing")
    
    # Check data
    cursor.execute("SELECT COUNT(*) FROM district_stats")
    count = cursor.fetchone()[0]
    if count > 0:
      print(f"   ℹ️  Database has {count} districts")
    else:
      print(f"   ℹ️  Database is empty (will return dummy data)")
    
    conn.close()
    return True
  
  except Exception as e:
    print(f"   ✗ Database error: {e}")
    return False

def check_environment():
  """Check environment variables."""
  print("\n🔧 Configuration")
  
  from utils.config import DATABASE_PATH, PORT
  
  print(f"   Database: {DATABASE_PATH}")
  print(f"   Port: {PORT}")
  print(f"   Flask Debug: {os.getenv('FLASK_ENV', 'development')}")
  print(f"   CORS: Enabled (all origins)")
  
  return True

def check_imports():
  """Check if main modules import correctly."""
  print("\n📂 Modules")
  
  modules = {
    "app": "app.py",
    "models.db": "models/db.py",
    "routes.districts": "routes/districts.py",
    "services.pipeline_service": "services/pipeline_service.py",
    "utils.geocoding": "utils/geocoding.py",
  }
  
  all_ok = True
  for module_name, file_path in modules.items():
    try:
      __import__(module_name)
      print(f"   ✓ {file_path}")
    except Exception as e:
      print(f"   ✗ {file_path} - {e}")
      all_ok = False
  
  return all_ok

def main():
  """Run all checks."""
  print("\n" + "="*60)
  print("🔍 BACKEND DIAGNOSTIC CHECK")
  print("="*60)
  
  results = {
    "Python Version": check_python_version(),
    "Dependencies": check_dependencies(),
    "Environment": check_environment(),
    "Modules": check_imports(),
    "Database": check_database(),
  }
  
  print("\n" + "="*60)
  print("📊 SUMMARY")
  print("="*60)
  
  passed = sum(results.values())
  total = len(results)
  
  for name, ok in results.items():
    status = "✓" if ok else "✗"
    print(f"   {status} {name}")
  
  print(f"\nResult: {passed}/{total} checks passed")
  
  if passed == total:
    print("\n✅ All checks passed!")
    print("\nYou can now run:")
    print("   python app.py")
  else:
    print(f"\n⚠️  {total - passed} checks failed")
    print("   Review issues above and install any missing dependencies:")
    print("   pip install -r requirements.txt")
  
  print("="*60 + "\n")

if __name__ == "__main__":
  main()
