from datetime import datetime
from typing import Any

from flask import Blueprint, current_app, request

from app.core.auth import jwt_required
from app.core.responses import api_response

bp = Blueprint("process_api", __name__)


def _map_status_to_frontend(status: str) -> str:
    normalized = (status or "").upper()
    if normalized == "CLEARED":
        return "cleared"
    if normalized == "INSPECTION":
        return "inspection"
    return "processing"


def _derive_overall_status(steps: list[dict[str, Any]]) -> str:
    complete_count = sum(1 for item in steps if str(item.get("status") or "").upper() == "COMPLETE")
    if complete_count >= 10:
        return "CLEARED"

    step6 = next((item for item in steps if int(item.get("step_no") or 0) == 6), None)
    if step6 and str(step6.get("status") or "").upper() == "COMPLETE":
        return "INSPECTION"

    return "PROCESSING"


@bp.get("/api/process/records")
@jwt_required()
def list_process_records():
    db = current_app.config["DB"]
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = max(int(request.args.get("offset", 0)), 0)
    q = (request.args.get("q") or "").strip()
    status = (request.args.get("status") or "").strip().upper()

    where_sql = ""
    params: list[Any] = []
    where_parts: list[str] = []
    if q:
        like = f"%{q}%"
        where_parts.append(
            "(bl_no LIKE "
            + db.placeholder
            + " OR goods_desc LIKE "
            + db.placeholder
            + " OR port_name LIKE "
            + db.placeholder
            + ")"
        )
        params.extend([like, like, like])
    if status in {"PROCESSING", "CLEARED", "INSPECTION"}:
        where_parts.append("overall_status = " + db.placeholder)
        params.append(status)

    if where_parts:
        where_sql = " WHERE " + " AND ".join(where_parts)

    with db.connection() as conn:
        rows = db.fetchall(
            conn,
            "SELECT id, bl_no, goods_desc, declaration_date, port_name, overall_status, created_time, updated_time "
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
            "bl": row["bl_no"],
            "goods_desc": row.get("goods_desc"),
            "declaration_date": row.get("declaration_date"),
            "port": row.get("port_name"),
            "status": _map_status_to_frontend(str(row.get("overall_status") or "")),
            "overall_status": row.get("overall_status"),
            "created_time": row.get("created_time"),
            "updated_time": row.get("updated_time"),
        }
        for row in rows
    ]

    return api_response(
        {
            "items": items,
            "total": int(total_row["total"] if total_row else 0),
            "limit": limit,
            "offset": offset,
        }
    )


@bp.get("/api/process/records/<int:record_id>")
@jwt_required()
def get_process_record(record_id: int):
    db = current_app.config["DB"]
    with db.connection() as conn:
        record = db.fetchone(
            conn,
            "SELECT id, bl_no, goods_desc, declaration_date, port_name, overall_status, created_time, updated_time "
            "FROM customs_process_record WHERE id = " + db.placeholder,
            [record_id],
        )
        if not record:
            return api_response({"error": "流程记录不存在"}, 404)

        steps = db.fetchall(
            conn,
            "SELECT id, step_no, status, completion_time, step_desc, created_time, updated_time "
            "FROM customs_process_step WHERE process_id = " + db.placeholder + " ORDER BY step_no ASC",
            [record_id],
        )

    complete_count = sum(1 for item in steps if str(item.get("status") or "").upper() == "COMPLETE")
    total_steps = len(steps)
    current_step = next((item for item in steps if str(item.get("status") or "").upper() != "COMPLETE"), None)

    return api_response(
        {
            "record": {
                "id": int(record["id"]),
                "bl": record.get("bl_no"),
                "goods_desc": record.get("goods_desc"),
                "declaration_date": record.get("declaration_date"),
                "port": record.get("port_name"),
                "status": _map_status_to_frontend(str(record.get("overall_status") or "")),
                "overall_status": record.get("overall_status"),
                "created_time": record.get("created_time"),
                "updated_time": record.get("updated_time"),
            },
            "steps": [
                {
                    "id": int(step["id"]),
                    "step_no": int(step["step_no"]),
                    "status": step.get("status"),
                    "date": step.get("completion_time") or "",
                    "desc": step.get("step_desc") or "",
                    "created_time": step.get("created_time"),
                    "updated_time": step.get("updated_time"),
                }
                for step in steps
            ],
            "progress": {
                "complete_count": complete_count,
                "total_count": total_steps,
                "percentage": round((complete_count / total_steps) * 100) if total_steps else 0,
                "current_step_no": int(current_step["step_no"]) if current_step else None,
            },
        }
    )


@bp.put("/api/process/records/<int:record_id>/steps/<int:step_no>")
@jwt_required("SUPER_ADMIN", "ADMIN", "CUSTOMS")
def update_process_step(record_id: int, step_no: int):
    if step_no < 1 or step_no > 10:
        return api_response({"error": "step_no 取值范围必须是 1-10"}, 400)

    payload = request.get_json(silent=True) or {}
    status = str(payload.get("status") or "").strip().upper()
    completion_time = payload.get("date")
    step_desc = payload.get("desc")

    if status not in {"COMPLETE", "PENDING"}:
        return api_response({"error": "status 必须是 COMPLETE 或 PENDING"}, 400)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db = current_app.config["DB"]
    with db.connection() as conn:
        record = db.fetchone(conn, "SELECT id FROM customs_process_record WHERE id = " + db.placeholder, [record_id])
        if not record:
            return api_response({"error": "流程记录不存在"}, 404)

        step = db.fetchone(
            conn,
            "SELECT id FROM customs_process_step WHERE process_id = " + db.placeholder + " AND step_no = " + db.placeholder,
            [record_id, step_no],
        )
        if not step:
            return api_response({"error": "流程步骤不存在"}, 404)

        db.update_by_id(
            conn,
            "customs_process_step",
            int(step["id"]),
            {
                "status": status,
                "completion_time": completion_time or None,
                "step_desc": step_desc,
                "updated_time": now_str,
            },
        )

        steps = db.fetchall(
            conn,
            "SELECT step_no, status FROM customs_process_step WHERE process_id = " + db.placeholder,
            [record_id],
        )
        overall_status = _derive_overall_status(steps)
        db.update_by_id(
            conn,
            "customs_process_record",
            record_id,
            {
                "overall_status": overall_status,
                "updated_time": now_str,
            },
        )

    return get_process_record(record_id)
