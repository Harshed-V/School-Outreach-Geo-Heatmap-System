import sqlite3
from utils.config import DATABASE_PATH


def get_connection():
  conn = sqlite3.connect(DATABASE_PATH)
  conn.row_factory = sqlite3.Row
  return conn


def init_db():
  conn = get_connection()
  cursor = conn.cursor()
  
  # Schools table with indexes for performance
  cursor.execute(
      """
      CREATE TABLE IF NOT EXISTS schools (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          district TEXT NOT NULL,
          lat REAL NOT NULL,
          lng REAL NOT NULL,
          type TEXT NOT NULL,
          student_count INTEGER DEFAULT 0
      )
      """
  )
  
  # Create index on district for faster queries
  cursor.execute(
      "CREATE INDEX IF NOT EXISTS idx_schools_district ON schools(district)"
  )
  
  # District statistics table
  cursor.execute(
      """
      CREATE TABLE IF NOT EXISTS district_stats (
          district TEXT PRIMARY KEY,
          total_schools INTEGER NOT NULL,
          higher_secondary_count INTEGER DEFAULT 0,
          total_students INTEGER DEFAULT 0,
          score INTEGER NOT NULL,
          lat REAL NOT NULL,
          lng REAL NOT NULL
      )
      """
  )

  columns = {
      row["name"]
      for row in cursor.execute("PRAGMA table_info(district_stats)").fetchall()
  }
  if "higher_secondary_count" not in columns:
    cursor.execute(
        "ALTER TABLE district_stats ADD COLUMN higher_secondary_count INTEGER DEFAULT 0"
    )
  if "total_students" not in columns:
    cursor.execute(
        "ALTER TABLE district_stats ADD COLUMN total_students INTEGER DEFAULT 0"
    )

  school_columns = {
      row["name"]
      for row in cursor.execute("PRAGMA table_info(schools)").fetchall()
  }
  if "student_count" not in school_columns:
    cursor.execute(
        "ALTER TABLE schools ADD COLUMN student_count INTEGER DEFAULT 0"
    )
  
  conn.commit()
  conn.close()
