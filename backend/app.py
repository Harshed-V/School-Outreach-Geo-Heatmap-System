import os
from flask import Flask
from flask_cors import CORS
from routes.districts import districts_bp
from utils.config import PORT


def create_app(run_pipeline_on_startup=True):
  """Create and configure Flask app with CORS and error handling.

  Args:
    run_pipeline_on_startup: If True, run the production data pipeline on app startup.
  """
  app = Flask(__name__)

  # Enable CORS for all routes - allows frontend at localhost:5173 to access backend.
  # In production, restrict to specific domains.
  CORS(app, resources={
      r"/api/*": {
          "origins": ["*"],
          "methods": ["GET", "POST", "OPTIONS"],
          "allow_headers": ["Content-Type"]
      }
  })

  @app.errorhandler(404)
  def not_found(error):
    return {"error": "Not Found", "message": "Endpoint does not exist"}, 404

  @app.errorhandler(500)
  def internal_error(error):
    return {"error": "Internal Server Error", "message": "The server encountered an error"}, 500

  app.register_blueprint(districts_bp)

  # NOTE: Data is now loaded directly by routes/districts.py from district_school_data.csv
  # at import time. The old pipeline_service is no longer used for the /api/districts route.
  if run_pipeline_on_startup:
    print("[APP] Data pipeline is handled by routes/districts.py directly (district_school_data.csv)")
    print("[APP] Skipping legacy pipeline_service startup call.")

  return app


# Create app with pipeline running on startup by default.
# Set RUN_PIPELINE_ON_STARTUP=false to disable.
run_on_startup = os.getenv("RUN_PIPELINE_ON_STARTUP", "true").lower() != "false"
app = create_app(run_pipeline_on_startup=run_on_startup)


if __name__ == "__main__":
  print("\n" + "=" * 70)
  print("SCHOOL OUTREACH GEO-HEATMAP SYSTEM - BACKEND")
  print("=" * 70)
  print(f"API Server: http://0.0.0.0:{PORT}")
  print(f"Frontend: http://localhost:5173 (when running npm run dev)")
  print("CORS: Enabled for all origins (development mode)")
  print("=" * 70 + "\n")
  app.run(host="0.0.0.0", port=PORT, debug=True, use_reloader=False)
