import json

from flask import Blueprint, current_app, g, request

from app.core.auth import jwt_required
from app.core.responses import api_response
from app.services.audit_finance_service import run_audit_review, run_finance_review

bp = Blueprint("ai_review_api", __name__)


def _loads_json(raw):
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


@bp.post("/api/audit/business/<int:business_id>/run")
@jwt_required("SUPER_ADMIN", "ADMIN", "CUSTOMS", "FINANCE")
def create_audit_run(business_id: int):
    payload = request.get_json(silent=True) or {}
    cost_record_id_raw = payload.get("cost_record_id")
    cost_record_id = None
    if cost_record_id_raw is not None:
        try:
            cost_record_id = int(cost_record_id_raw)
        except Exception:
            return api_response({"error": "cost_record_id 必须是整数"}, 400)

    db = current_app.config["DB"]
    try:
        run = run_audit_review(
            db,
            business_id=business_id,
            cost_record_id=cost_record_id,
            created_by=int(g.current_user["id"]),
        )
    except LookupError as exc:
        return api_response({"error": str(exc)}, 404)
    except ValueError as exc:
        return api_response({"error": str(exc)}, 400)

    return api_response({"run": run}, 201)


@bp.get("/api/audit/runs")
@jwt_required()
def list_audit_runs():
    db = current_app.config["DB"]
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
    except Exception:
        return api_response({"error": "limit/offset 必须是整数"}, 400)

    business_id_raw = request.args.get("business_id")
    status = (request.args.get("status") or "").strip().upper()

    where_parts: list[str] = []
    params = []
    if business_id_raw:
        try:
            business_id = int(business_id_raw)
        except Exception:
            return api_response({"error": "business_id 必须是整数"}, 400)
        where_parts.append("business_id = " + db.placeholder)
        params.append(business_id)
    if status:
        where_parts.append("status = " + db.placeholder)
        params.append(status)

    where_sql = " WHERE " + " AND ".join(where_parts) if where_parts else ""

    with db.connection() as conn:
        rows = db.fetchall(
            conn,
            "SELECT id, business_id, cost_record_id, source, model_name, status, risk_level, score, summary, error_message, created_by, created_time, updated_time "
            "FROM ai_audit_run"
            + where_sql
            + " ORDER BY id DESC LIMIT "
            + db.placeholder
            + " OFFSET "
            + db.placeholder,
            params + [limit, offset],
        )
        total_row = db.fetchone(conn, "SELECT COUNT(*) AS total FROM ai_audit_run" + where_sql, params)

    items = [
        {
            "id": int(row["id"]),
            "business_id": int(row["business_id"]),
            "cost_record_id": row.get("cost_record_id"),
            "source": row.get("source"),
            "model_name": row.get("model_name"),
            "status": row.get("status"),
            "risk_level": row.get("risk_level"),
            "score": float(row.get("score") or 0),
            "summary": row.get("summary"),
            "error_message": row.get("error_message"),
            "created_by": row.get("created_by"),
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


@bp.get("/api/audit/runs/<int:run_id>")
@jwt_required()
def get_audit_run(run_id: int):
    db = current_app.config["DB"]
    with db.connection() as conn:
        run_row = db.fetchone(conn, "SELECT * FROM ai_audit_run WHERE id = " + db.placeholder, [run_id])
        if not run_row:
            return api_response({"error": "审计记录不存在"}, 404)

        findings = db.fetchall(
            conn,
            "SELECT id, finding_type, severity, rule_code, title, description, evidence, suggestion, amount, created_time "
            "FROM ai_audit_finding WHERE audit_run_id = "
            + db.placeholder
            + " ORDER BY id ASC",
            [run_id],
        )

    return api_response(
        {
            "run": {
                **run_row,
                "checks": _loads_json(run_row.get("checks_json")) or [],
                "input_snapshot": _loads_json(run_row.get("input_json")) or {},
                "findings": findings,
            }
        }
    )


@bp.post("/api/finance/cost-records/<int:cost_record_id>/review")
@jwt_required("SUPER_ADMIN", "ADMIN", "FINANCE")
def create_finance_review(cost_record_id: int):
    db = current_app.config["DB"]
    try:
        review = run_finance_review(db, cost_record_id=cost_record_id, created_by=int(g.current_user["id"]))
    except LookupError as exc:
        return api_response({"error": str(exc)}, 404)
    except ValueError as exc:
        return api_response({"error": str(exc)}, 400)

    return api_response({"review": review}, 201)


@bp.get("/api/finance/reviews")
@jwt_required()
def list_finance_reviews():
    db = current_app.config["DB"]
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
    except Exception:
        return api_response({"error": "limit/offset 必须是整数"}, 400)

    cost_record_id_raw = request.args.get("cost_record_id")
    status = (request.args.get("status") or "").strip().upper()
    where_parts: list[str] = []
    params = []
    if cost_record_id_raw:
        try:
            cost_record_id = int(cost_record_id_raw)
        except Exception:
            return api_response({"error": "cost_record_id 必须是整数"}, 400)
        where_parts.append("cost_record_id = " + db.placeholder)
        params.append(cost_record_id)
    if status:
        where_parts.append("status = " + db.placeholder)
        params.append(status)
    where_sql = " WHERE " + " AND ".join(where_parts) if where_parts else ""

    with db.connection() as conn:
        rows = db.fetchall(
            conn,
            "SELECT id, cost_record_id, source, model_name, status, health_level, score, summary, error_message, created_by, created_time, updated_time "
            "FROM ai_finance_review"
            + where_sql
            + " ORDER BY id DESC LIMIT "
            + db.placeholder
            + " OFFSET "
            + db.placeholder,
            params + [limit, offset],
        )
        total_row = db.fetchone(conn, "SELECT COUNT(*) AS total FROM ai_finance_review" + where_sql, params)

    items = [
        {
            "id": int(row["id"]),
            "cost_record_id": int(row["cost_record_id"]),
            "source": row.get("source"),
            "model_name": row.get("model_name"),
            "status": row.get("status"),
            "health_level": row.get("health_level"),
            "score": float(row.get("score") or 0),
            "summary": row.get("summary"),
            "error_message": row.get("error_message"),
            "created_by": row.get("created_by"),
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


@bp.get("/api/finance/reviews/<int:review_id>")
@jwt_required()
def get_finance_review(review_id: int):
    db = current_app.config["DB"]
    with db.connection() as conn:
        review_row = db.fetchone(conn, "SELECT * FROM ai_finance_review WHERE id = " + db.placeholder, [review_id])
        if not review_row:
            return api_response({"error": "财务分析记录不存在"}, 404)
        items = db.fetchall(
            conn,
            "SELECT id, severity, title, description, recommendation, created_time "
            "FROM ai_finance_item WHERE finance_review_id = "
            + db.placeholder
            + " ORDER BY id ASC",
            [review_id],
        )
    return api_response(
        {
            "review": {
                **review_row,
                "metrics": _loads_json(review_row.get("metrics_json")) or {},
                "input_snapshot": _loads_json(review_row.get("input_json")) or {},
                "items": items,
            }
        }
    )
