from flask import Blueprint, current_app

from app.core.responses import api_response

bp = Blueprint("health_api", __name__)


@bp.get("/api/health")
def health():
    db = current_app.config["DB"]
    return api_response({"status": "ok", "database": db.backend})
