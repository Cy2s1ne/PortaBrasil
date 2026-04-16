from typing import Any

from flask import Blueprint, current_app, request

from app.core.auth import jwt_required
from app.core.responses import api_response

bp = Blueprint("reports_api", __name__)


def _status_to_frontend(status: str) -> str:
    normalized = (status or "").upper()
    if normalized == "CLEARED":
        return "cleared"
    if normalized == "INSPECTION":
        return "inspection"
    return "processing"


@bp.get("/api/reports/records")
@jwt_required()
def list_report_records():
    db = current_app.config["DB"]
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = max(int(request.args.get("offset", 0)), 0)
    q = (request.args.get("q") or "").strip()

    where_sql = ""
    params: list[Any] = []
    if q:
        like = f"%{q}%"
        where_sql = (
            " WHERE (bl_no LIKE "
            + db.placeholder
            + " OR goods_desc LIKE "
            + db.placeholder
            + " OR port_name LIKE "
            + db.placeholder
            + ")"
        )
        params.extend([like, like, like])

    with db.connection() as conn:
        rows = db.fetchall(
            conn,
            "SELECT id, bl_no, goods_desc, declaration_date, port_name, overall_status, updated_time "
            "FROM customs_process_record"
            + where_sql
            + " ORDER BY declaration_date DESC, id DESC LIMIT "
            + db.placeholder
            + " OFFSET "
            + db.placeholder,
            params + [limit, offset],
        )
        total_row = db.fetchone(conn, "SELECT COUNT(*) AS total FROM customs_process_record" + where_sql, params)

    items = [
        {
            "id": int(row["id"]),
            "bl": row.get("bl_no"),
            "goods_desc": row.get("goods_desc"),
            "declaration_date": row.get("declaration_date"),
            "port": row.get("port_name"),
            "status": _status_to_frontend(str(row.get("overall_status") or "")),
            "overall_status": row.get("overall_status"),
            "updated_time": row.get("updated_time"),
        }
        for row in rows
    ]

    return api_response({"items": items, "total": int(total_row["total"] if total_row else 0), "limit": limit, "offset": offset})
