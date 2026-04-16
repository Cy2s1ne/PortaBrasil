from flask import Blueprint, current_app

from app.core.auth import jwt_required
from app.core.responses import api_response

bp = Blueprint("dashboard_api", __name__)


@bp.get("/api/dashboard/overview")
@jwt_required()
def get_dashboard_overview():
    db = current_app.config["DB"]

    with db.connection() as conn:
        status_count_rows = db.fetchall(
            conn,
            "SELECT overall_status, COUNT(*) AS total FROM customs_process_record GROUP BY overall_status",
        )
        status_count = {str(row["overall_status"]): int(row["total"] or 0) for row in status_count_rows}

        total_row = db.fetchone(conn, "SELECT COUNT(*) AS total FROM customs_process_record")
        total_records = int(total_row["total"] if total_row else 0)

        taxes_row = db.fetchone(conn, "SELECT COALESCE(SUM(CAST(total_debit AS REAL)), 0) AS taxes_due FROM customs_business")
        taxes_due = float(taxes_row["taxes_due"] if taxes_row else 0)

        step_rows = db.fetchall(
            conn,
            "SELECT step_no, COUNT(*) AS total FROM customs_process_step WHERE status = 'COMPLETE' GROUP BY step_no ORDER BY step_no",
        )
        step_count_map = {int(row["step_no"]): int(row["total"] or 0) for row in step_rows}

        activities = db.fetchall(
            conn,
            "SELECT id, activity_type, title, description, occurred_at FROM customs_activity ORDER BY occurred_at DESC, id DESC LIMIT 10",
        )

    kanban_items = [{"step_no": step_no, "count": step_count_map.get(step_no, 0)} for step_no in range(1, 11)]
    anomaly = status_count.get("INSPECTION", 0)

    return api_response(
        {
            "stats": {
                "in_progress": status_count.get("PROCESSING", 0),
                "taxes_due": round(taxes_due, 2),
                "anomaly": anomaly,
                "done_month": status_count.get("CLEARED", 0),
            },
            "kanban": {
                "items": kanban_items,
                "total": total_records,
                "normal": max(total_records - anomaly, 0),
                "anomaly": anomaly,
            },
            "activities": [
                {
                    "id": int(item["id"]),
                    "type": item.get("activity_type"),
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "time": item.get("occurred_at"),
                }
                for item in activities
            ],
        }
    )
