import os
from flask import Flask
from flask_cors import CORS
from routes.districts import districts_bp

def create_app():
    """Application factory for the School Outreach API."""
    app = Flask(__name__)

    # 9. Enable CORS for frontend integration
    CORS(app)

    # 8. Clean up development-only code / test routes
    # Register API blueprints
    app.register_blueprint(districts_bp)

    # 7. Robust error handling for production
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not Found", "message": "The requested endpoint does not exist"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal Server Error", "message": "An unexpected error occurred on the server"}, 500

    @app.route("/health")
    def health_check():
        return {"status": "healthy", "service": "school-outreach-backend"}, 200

    return app

# 1. Flask instance named 'app' for Gunicorn (gunicorn app:app)
app = create_app()

# 1. Standard production startup block
if __name__ == "__main__":
    # 4. Use dynamic port from environment with fallback
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

