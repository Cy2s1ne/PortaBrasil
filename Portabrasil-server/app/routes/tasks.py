from flask import Blueprint, current_app

from app.core.auth import jwt_required
from app.core.responses import api_response

bp = Blueprint("tasks_api", __name__)


@bp.get("/api/tasks/<int:task_id>")
@jwt_required()
def get_task(task_id: int):
    db = current_app.config["DB"]
    with db.connection() as conn:
        task = db.fetchone(conn, "SELECT * FROM pdf_parse_task WHERE id = " + db.placeholder, [task_id])
        if not task:
            return api_response({"error": "任务不存在"}, 404)
    return api_response({"task": task})
