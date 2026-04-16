from typing import Any

from flask import Blueprint, current_app, request

from app.core.auth import jwt_required
from app.core.responses import api_response

bp = Blueprint("business_api", __name__)


@bp.get("/api/business")
@jwt_required()
def list_business():
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = max(int(request.args.get("offset", 0)), 0)
    search = request.args.get("q")
    params: list[Any] = []
    where = ""
    db = current_app.config["DB"]
    if search:
        like = f"%{search}%"
        where = (
            " WHERE s_ref LIKE "
            + db.placeholder
            + " OR invoice_no LIKE "
            + db.placeholder
            + " OR customer_name LIKE "
            + db.placeholder
            + " OR mawb_mbl LIKE "
            + db.placeholder
        )
        params.extend([like, like, like, like])

    with db.connection() as conn:
        rows = db.fetchall(
            conn,
            f"SELECT * FROM customs_business{where} ORDER BY updated_time DESC, id DESC LIMIT {db.placeholder} OFFSET {db.placeholder}",
            params + [limit, offset],
        )
        total = db.fetchone(conn, f"SELECT COUNT(*) AS total FROM customs_business{where}", params)
    return api_response({"items": rows, "total": total["total"] if total else 0, "limit": limit, "offset": offset})


@bp.get("/api/business/<int:business_id>")
@jwt_required()
def get_business(business_id: int):
    db = current_app.config["DB"]
    with db.connection() as conn:
        business = db.fetchone(conn, "SELECT * FROM customs_business WHERE id = " + db.placeholder, [business_id])
        if not business:
            return api_response({"error": "业务记录不存在"}, 404)
        fees = db.fetchall(
            conn,
            "SELECT * FROM customs_business_fee_item WHERE business_id = "
            + db.placeholder
            + " ORDER BY line_no, id",
            [business_id],
        )
    business["fee_items"] = fees
    return api_response({"business": business})


@bp.get("/api/business/<int:business_id>/fees")
@jwt_required()
def list_fees(business_id: int):
    db = current_app.config["DB"]
    with db.connection() as conn:
        business = db.fetchone(conn, "SELECT id FROM customs_business WHERE id = " + db.placeholder, [business_id])
        if not business:
            return api_response({"error": "业务记录不存在"}, 404)
        fees = db.fetchall(
            conn,
            "SELECT * FROM customs_business_fee_item WHERE business_id = "
            + db.placeholder
            + " ORDER BY line_no, id",
            [business_id],
        )
    return api_response({"items": fees, "total": len(fees)})
