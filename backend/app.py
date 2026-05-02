import os
import logging
from flask import Flask
from flask_cors import CORS
from routes.districts import districts_bp

# 8. Logging - Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory for the School Outreach API."""
    app = Flask(__name__)

    # 9. Performance - No blocking operations during startup
    # CORS enabled for frontend integration
    CORS(app)

    # Register API blueprints
    app.register_blueprint(districts_bp)

    # 7. Error handling - Return clean API responses
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not Found", "message": "The requested endpoint does not exist"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal Server Error", "message": "An unexpected error occurred"}, 500

    @app.route("/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "school-outreach-backend",
            "version": "1.1.0"
        }, 200

    logger.info("Application factory created successfully.")
    return app

# 1. Gunicorn compatibility - Flask instance named 'app'
app = create_app()

# 1. Standard production startup block
if __name__ == "__main__":
    logger.info("Starting Flask development server...")
    # 4. Correct binding to PORT using environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

