import os

from flask import Flask

from app.core.responses import api_response
from app.routes.ai_review import bp as ai_review_bp
from app.routes.auth import bp as auth_bp
from app.routes.business import bp as business_bp
from app.routes.cost import bp as cost_bp
from app.routes.dashboard import bp as dashboard_bp
from app.routes.documents import bp as documents_bp
from app.routes.files import bp as files_bp
from app.routes.health import bp as health_bp
from app.routes.process import bp as process_bp
from app.routes.reports import bp as reports_bp
from app.routes.tasks import bp as tasks_bp
from database import get_database

try:
    from flask_cors import CORS
except Exception:
    CORS = None


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
    app.config["JWT_ALGORITHM"] = "HS256"
    app.config["JWT_EXPIRES_MINUTES"] = int(os.getenv("JWT_EXPIRES_MINUTES", "120"))
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "change-this-in-production-use-at-least-32-bytes-secret")
    app.config["DEFAULT_REGISTER_ROLE"] = os.getenv("DEFAULT_REGISTER_ROLE", "FORWARDER").strip().upper() or "FORWARDER"

    if CORS:
        CORS(app, resources={r"/api/*": {"origins": "*"}})
    else:

        @app.after_request
        def add_cors_headers(response):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            return response

    db = get_database()
    db.initialize()
    app.config["DB"] = db

    @app.errorhandler(Exception)
    def handle_error(error):
        status = getattr(error, "code", 500)
        if status < 400:
            status = 500
        return api_response({"error": str(error)}, status)

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(business_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(process_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(cost_bp)
    app.register_blueprint(ai_review_bp)

    return app
