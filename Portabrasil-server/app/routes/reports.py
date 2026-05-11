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


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, str) and not value.strip():
            return default
        return float(value)
    except Exception:
        return default


def _serialize_record(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": int(row["id"]),
        "business_id": row.get("business_id"),
        "bl": row.get("bl_no"),
        "goods_desc": row.get("goods_desc"),
        "declaration_date": row.get("declaration_date"),
        "port": row.get("port_name"),
        "status": _status_to_frontend(str(row.get("overall_status") or "")),
        "overall_status": row.get("overall_status"),
        "created_time": row.get("created_time"),
        "updated_time": row.get("updated_time"),
    }


@bp.get("/api/reports/records")
@jwt_required("SUPER_ADMIN", "ADMIN", "FORWARDER")
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
            "SELECT id, business_id, bl_no, goods_desc, declaration_date, port_name, overall_status, created_time, updated_time "
            "FROM customs_process_record"
            + where_sql
            + " ORDER BY declaration_date DESC, id DESC LIMIT "
            + db.placeholder
            + " OFFSET "
            + db.placeholder,
            params + [limit, offset],
        )
        total_row = db.fetchone(conn, "SELECT COUNT(*) AS total FROM customs_process_record" + where_sql, params)

    items = [_serialize_record(row) for row in rows]

    return api_response({"items": items, "total": int(total_row["total"] if total_row else 0), "limit": limit, "offset": offset})


@bp.get("/api/reports/records/<int:record_id>")
@jwt_required("SUPER_ADMIN", "ADMIN", "FORWARDER")
def get_report_record(record_id: int):
    db = current_app.config["DB"]
    with db.connection() as conn:
        record = db.fetchone(
            conn,
            "SELECT id, business_id, bl_no, goods_desc, declaration_date, port_name, overall_status, created_time, updated_time "
            "FROM customs_process_record WHERE id = " + db.placeholder,
            [record_id],
        )
        if not record:
            return api_response({"error": "报表记录不存在"}, 404)

        steps = db.fetchall(
            conn,
            "SELECT id, step_no, status, completion_time, step_desc, created_time, updated_time "
            "FROM customs_process_step WHERE process_id = " + db.placeholder + " ORDER BY step_no ASC",
            [record_id],
        )

        business = None
        fee_items: list[dict[str, Any]] = []
        if record.get("business_id"):
            business = db.fetchone(conn, "SELECT * FROM customs_business WHERE id = " + db.placeholder, [record["business_id"]])
            if business:
                fee_items = db.fetchall(
                    conn,
                    "SELECT id, fee_date, fee_code, fee_name, credit_amount, debit_amount, line_no, raw_text, created_time "
                    "FROM customs_business_fee_item WHERE business_id = "
                    + db.placeholder
                    + " ORDER BY line_no ASC, id ASC",
                    [record["business_id"]],
                )

    complete_count = sum(1 for item in steps if str(item.get("status") or "").upper() == "COMPLETE")
    total_steps = len(steps)
    current_step = next((item for item in steps if str(item.get("status") or "").upper() != "COMPLETE"), None)
    total_credit = sum(_to_float(item.get("credit_amount")) for item in fee_items)
    total_debit = sum(_to_float(item.get("debit_amount")) for item in fee_items)

    return api_response(
        {
            "record": _serialize_record(record),
            "business": business,
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
            "fee_items": fee_items,
            "fee_summary": {
                "total_credit": round(total_credit, 2),
                "total_debit": round(total_debit, 2),
                "balance": round(total_credit - total_debit, 2),
            },
        }
    )
