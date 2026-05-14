from datetime import datetime

from flask import Blueprint, current_app, g

from app.core.auth import jwt_required
from app.core.responses import api_response
from services import sync_missing_process_records

bp = Blueprint("dashboard_api", __name__)

ADMIN_ROLES = {"SUPER_ADMIN", "ADMIN"}
ROLE_ACTIVITY_KEYWORDS = {
    "FORWARDER": (
        "到港",
        "提单",
        "集装箱",
        "流程",
        "查验",
        "放行",
        "提货",
        "运输",
        "配送",
        "税费",
        "关税",
        "container",
        "process",
        "inspection",
        "release",
        "pickup",
        "tax",
        "duty",
    ),
    "CUSTOMS": (
        "海关",
        "申报",
        "文件",
        "单据",
        "审核",
        "查验",
        "放行",
        "siscomex",
        "customs",
        "declaration",
        "document",
        "inspection",
        "release",
    ),
    "FINANCE": (
        "税费",
        "关税",
        "费用",
        "成本",
        "财务",
        "付款",
        "支付",
        "退款",
        "借方",
        "贷方",
        "余额",
        "复核",
        "tax",
        "duty",
        "fee",
        "cost",
        "finance",
        "payment",
        "refund",
        "debit",
        "credit",
        "balance",
    ),
}


def _activity_matches_roles(activity: dict, roles: set[str]) -> bool:
    if roles.intersection(ADMIN_ROLES):
        return True

    text = " ".join(
        str(activity.get(field) or "")
        for field in ("activity_type", "title", "description")
    ).lower()
    keywords: list[str] = []
    for role in roles:
        keywords.extend(ROLE_ACTIVITY_KEYWORDS.get(role, ()))

    return any(keyword.lower() in text for keyword in keywords)


@bp.get("/api/dashboard/overview")
@jwt_required()
def get_dashboard_overview():
    db = current_app.config["DB"]
    month_prefix = datetime.now().strftime("%Y-%m")
    current_roles = set(g.current_user.get("roles") or [])

    with db.connection() as conn:
        sync_missing_process_records(db, conn)
        status_count_rows = db.fetchall(
            conn,
            "SELECT overall_status, COUNT(*) AS total FROM customs_process_record GROUP BY overall_status",
        )
        status_count = {str(row["overall_status"]): int(row["total"] or 0) for row in status_count_rows}

        process_rows = db.fetchall(conn, "SELECT id, overall_status FROM customs_process_record")
        total_records = len(process_rows)

        done_month_row = db.fetchone(
            conn,
            "SELECT COUNT(*) AS total FROM customs_process_record "
            "WHERE overall_status = 'CLEARED' AND COALESCE(declaration_date, created_time) LIKE "
            + db.placeholder,
            [f"{month_prefix}%"],
        )
        done_month = int(done_month_row["total"] if done_month_row else 0)

        taxes_row = db.fetchone(conn, "SELECT COALESCE(SUM(total_debit), 0) AS taxes_due FROM customs_business")
        taxes_due = float(taxes_row["taxes_due"] if taxes_row else 0)

        step_status_rows = db.fetchall(
            conn,
            "SELECT process_id, step_no, status FROM customs_process_step ORDER BY process_id ASC, step_no ASC",
        )

        activities = db.fetchall(
            conn,
            "SELECT id, activity_type, title, description, occurred_at FROM customs_activity ORDER BY occurred_at DESC, id DESC LIMIT 50",
        )

    steps_by_process: dict[int, list[dict]] = {}
    for step in step_status_rows:
        steps_by_process.setdefault(int(step["process_id"]), []).append(step)

    step_count_map = {step_no: 0 for step_no in range(1, 11)}
    for process in process_rows:
        process_id = int(process["id"])
        steps = steps_by_process.get(process_id, [])
        current_step = next(
            (int(step["step_no"]) for step in steps if str(step.get("status") or "").upper() != "COMPLETE"),
            10,
        )
        step_count_map[current_step] = step_count_map.get(current_step, 0) + 1

    kanban_items = [{"step_no": step_no, "count": step_count_map.get(step_no, 0)} for step_no in range(1, 11)]
    anomaly = status_count.get("INSPECTION", 0)

    role_activities = [
        item for item in activities
        if _activity_matches_roles(item, current_roles)
    ][:10]

    return api_response(
        {
            "stats": {
                "in_progress": status_count.get("PROCESSING", 0),
                "taxes_due": round(taxes_due, 2),
                "anomaly": anomaly,
                "done_month": done_month,
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
                for item in role_activities
            ],
        }
    )
