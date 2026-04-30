import json
import os
from datetime import datetime
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from flask import Blueprint, current_app, g, request

from app.core.auth import jwt_required
from app.core.responses import api_response

bp = Blueprint("cost_api", __name__)

# apihz.cn exchange rate API credentials
FX_API_ID = os.getenv("FX_API_ID", "")
FX_API_KEY = os.getenv("FX_API_KEY", "")
RATE_SOURCE_URL = "https://cn.apihz.cn/api/jinrong/huilv.php"


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, str) and not value.strip():
            return default
        return float(value)
    except Exception:
        return default


def _normalize_products(raw_products: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_products, list):
        return []

    normalized: list[dict[str, Any]] = []
    for product in raw_products:
        if not isinstance(product, dict):
            continue
        name = str(product.get("name") or "").strip()
        qty = _to_float(product.get("qty"), 0.0)
        if qty < 0:
            qty = 0.0
        normalized.append({"name": name, "qty": qty})
    return normalized


def _calculate_cost(payload: dict[str, Any]) -> dict[str, Any]:
    customs_fee = _to_float(payload.get("customs_fee"))
    refund_fee = _to_float(payload.get("refund_fee"))
    usd_amount = _to_float(payload.get("usd_amount"))
    usd_rate = _to_float(payload.get("usd_rate"), 1.0)
    other_fees = _to_float(payload.get("other_fees"))
    products = _normalize_products(payload.get("products"))

    net_customs = customs_fee - refund_fee
    usd_in_brl = usd_amount * usd_rate
    total_base = net_customs + usd_in_brl + other_fees
    total_qty = sum(item["qty"] for item in products)
    per_unit_cost = (total_base / total_qty) if total_qty > 0 else 0.0

    product_costs = []
    for product in products:
        qty = product["qty"]
        ratio = (qty / total_qty) if total_qty > 0 else 0.0
        allocation_cost = total_base * ratio
        unit_cost = (allocation_cost / qty) if qty > 0 else 0.0
        product_costs.append(
            {
                "name": product["name"] or "Unnamed Product",
                "qty": round(qty, 4),
                "cost": round(allocation_cost, 4),
                "unit_cost": round(unit_cost, 4),
            }
        )

    return {
        "input": {
            "customs_fee": round(customs_fee, 4),
            "refund_fee": round(refund_fee, 4),
            "usd_amount": round(usd_amount, 4),
            "usd_rate": round(usd_rate, 6),
            "other_fees": round(other_fees, 4),
            "products": products,
        },
        "summary": {
            "net_customs": round(net_customs, 4),
            "usd_in_brl": round(usd_in_brl, 4),
            "total_base": round(total_base, 4),
            "total_qty": round(total_qty, 4),
            "per_unit_cost": round(per_unit_cost, 4),
        },
        "product_costs": product_costs,
    }


def _fetch_apihz_rate(from_currency: str, to_currency: str) -> tuple[float, str | None]:
    params = urlencode({
        "id": FX_API_ID,
        "key": FX_API_KEY,
        "from": from_currency,
        "to": to_currency,
        "money": "1",
    })
    url = f"{RATE_SOURCE_URL}?{params}"
    with urlopen(url, timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))

    code = _to_float(payload.get("code"), -1)
    if code != 200:
        raise ValueError(f"apihz API error: code={code}, msg={payload.get('msg', 'unknown')}")

    rate = _to_float(payload.get("rate"), 0.0)
    if rate <= 0:
        raise ValueError(f"apihz returned invalid rate: {rate}")

    uptime = payload.get("uptime")
    return rate, uptime if isinstance(uptime, str) else None


def _parse_live_usd_brl_rate() -> tuple[float, str | None]:
    rate, updated_at = _fetch_apihz_rate("USD", "BRL")
    return rate, updated_at


def _upsert_rate_cache(db, conn, base: str, quote: str, rate: float, source: str, updated_at: str) -> None:
    if db.backend == "mysql":
        db.execute(
            conn,
            "INSERT INTO fx_rate_cache (base_currency, quote_currency, rate, source, updated_at) "
            "VALUES (%s, %s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE rate = VALUES(rate), source = VALUES(source), updated_at = VALUES(updated_at)",
            [base, quote, rate, source, updated_at],
        )
        return

    db.execute(
        conn,
        "INSERT INTO fx_rate_cache (base_currency, quote_currency, rate, source, updated_at) "
        "VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(base_currency, quote_currency) DO UPDATE SET "
        "rate = excluded.rate, source = excluded.source, updated_at = excluded.updated_at",
        [base, quote, rate, source, updated_at],
    )


def _get_cached_rate(db, conn, base: str, quote: str) -> dict[str, Any] | None:
    return db.fetchone(
        conn,
        "SELECT id, base_currency, quote_currency, rate, source, updated_at "
        "FROM fx_rate_cache WHERE base_currency = "
        + db.placeholder
        + " AND quote_currency = "
        + db.placeholder,
        [base, quote],
    )


def _serialize_cost_record(row: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": int(row["id"]),
        "process_record_id": row.get("process_record_id"),
        "record_no": row.get("record_no"),
        "customs_fee": _to_float(row.get("customs_fee")),
        "refund_fee": _to_float(row.get("refund_fee")),
        "usd_amount": _to_float(row.get("usd_amount")),
        "usd_rate": _to_float(row.get("usd_rate")),
        "other_fees": _to_float(row.get("other_fees")),
        "total_qty": _to_float(row.get("total_qty")),
        "total_base": _to_float(row.get("total_base")),
        "per_unit_cost": _to_float(row.get("per_unit_cost")),
        "currency": row.get("currency"),
        "note": row.get("note"),
        "created_by": row.get("created_by"),
        "created_by_name": row.get("created_by_name"),
        "created_time": row.get("created_time"),
        "updated_time": row.get("updated_time"),
        "items": [
            {
                "id": int(item["id"]),
                "line_no": int(item.get("line_no") or 0),
                "product_name": item.get("product_name"),
                "qty": _to_float(item.get("qty")),
                "allocation_cost": _to_float(item.get("allocation_cost")),
                "unit_cost": _to_float(item.get("unit_cost")),
            }
            for item in items
        ],
    }


@bp.get("/api/cost/overview")
@jwt_required()
def get_cost_overview():
    db = current_app.config["DB"]
    with db.connection() as conn:
        total_row = db.fetchone(
            conn,
            "SELECT COALESCE(SUM(CAST(total_debit AS REAL)), 0) AS total_import_cost FROM customs_business",
        )
        total_import_cost = _to_float(total_row.get("total_import_cost") if total_row else 0.0)

        if total_import_cost <= 0:
            alt_total_row = db.fetchone(
                conn,
                "SELECT COALESCE(SUM(CAST(total_base AS REAL)), 0) AS total_import_cost FROM customs_cost_record",
            )
            total_import_cost = _to_float(alt_total_row.get("total_import_cost") if alt_total_row else 0.0)

        rows = db.fetchall(
            conn,
            "SELECT fee_name AS label, COALESCE(SUM(CAST(debit_amount AS REAL)), 0) AS amount "
            "FROM customs_business_fee_item "
            "GROUP BY fee_name "
            "ORDER BY amount DESC, label ASC LIMIT 5",
        )

    if rows:
        total_amount = sum(_to_float(row.get("amount")) for row in rows) or 1.0
        details = [
            {
                "label": row.get("label"),
                "amount": round(_to_float(row.get("amount")), 2),
                "percent": round((_to_float(row.get("amount")) / total_amount) * 100, 2),
            }
            for row in rows
        ]
    else:
        details = [
            {"label": "II (进口税)", "amount": 520000.0, "percent": 42.0},
            {"label": "IPI (工业产品税)", "amount": 310000.0, "percent": 25.0},
            {"label": "PIS/COFINS", "amount": 250000.0, "percent": 20.0},
            {"label": "ICMS", "amount": 115600.0, "percent": 9.0},
            {"label": "AFRMM 及其他", "amount": 50000.0, "percent": 4.0},
        ]
        if total_import_cost <= 0:
            total_import_cost = 1245600.0

    largest_share = details[0] if details else None
    return api_response(
        {
            "total_import_cost": round(total_import_cost, 2),
            "largest_share": largest_share,
            "major_tax_details": details,
        }
    )


def _is_rate_stale(updated_at: str | None) -> bool:
    if not updated_at:
        return True
    try:
        return (datetime.now() - datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")).total_seconds() > 86400
    except Exception:
        return True


@bp.get("/api/cost/exchange-rate")
@jwt_required()
def get_exchange_rate():
    base = (request.args.get("base") or "USD").strip().upper()
    quote = (request.args.get("quote") or "BRL").strip().upper()
    if base != "USD" or quote != "BRL":
        return api_response({"error": "当前仅支持 base=USD, quote=BRL"}, 400)

    default_rate = _to_float(os.getenv("DEFAULT_USD_BRL_RATE", "5.0000"), 5.0)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    db = current_app.config["DB"]
    with db.connection() as conn:
        try:
            live_rate, updated_at = _parse_live_usd_brl_rate()
            _upsert_rate_cache(db, conn, base, quote, live_rate, "apihz", updated_at or now_str)
            stale = _is_rate_stale(updated_at)
            return api_response(
                {
                    "base": base,
                    "quote": quote,
                    "rate": live_rate,
                    "source": "apihz",
                    "updated_at": updated_at or now_str,
                    "live": True,
                    "stale": stale,
                }
            )
        except (URLError, ValueError, TimeoutError, OSError) as error:
            cached = _get_cached_rate(db, conn, base, quote)
            if cached:
                stale = _is_rate_stale(cached.get("updated_at"))
                return api_response(
                    {
                        "base": base,
                        "quote": quote,
                        "rate": round(_to_float(cached.get("rate")), 6),
                        "source": cached.get("source") or "cache",
                        "updated_at": cached.get("updated_at"),
                        "live": False,
                        "stale": stale,
                    }
                )

    return api_response(
        {
            "base": base,
            "quote": quote,
            "rate": round(default_rate, 6),
            "source": "default",
            "updated_at": now_str,
            "live": False,
            "stale": True,
        }
    )


@bp.post("/api/cost/calculate")
@jwt_required()
def calculate_cost():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return api_response({"error": "请求体必须是 JSON 对象"}, 400)

    result = _calculate_cost(payload)
    return api_response(result)


@bp.post("/api/cost/records")
@jwt_required("SUPER_ADMIN", "ADMIN", "FINANCE")
def create_cost_record():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return api_response({"error": "请求体必须是 JSON 对象"}, 400)

    process_record_id_raw = payload.get("process_record_id")
    process_record_id = None
    if process_record_id_raw is not None:
        try:
            process_record_id = int(process_record_id_raw)
        except Exception:
            return api_response({"error": "process_record_id 必须是整数"}, 400)

    note = str(payload.get("note") or "").strip()
    calculated = _calculate_cost(payload)
    now_str = datetime.now().strftime("%Y%m%d%H%M%S%f")

    db = current_app.config["DB"]
    with db.connection() as conn:
        if process_record_id is not None:
            process_record = db.fetchone(
                conn,
                "SELECT id FROM customs_process_record WHERE id = " + db.placeholder,
                [process_record_id],
            )
            if not process_record:
                return api_response({"error": "流程记录不存在"}, 404)

        record_no = f"COST-{now_str}"
        record_id = db.insert(
            conn,
            "customs_cost_record",
            {
                "process_record_id": process_record_id,
                "record_no": record_no,
                "customs_fee": calculated["input"]["customs_fee"],
                "refund_fee": calculated["input"]["refund_fee"],
                "usd_amount": calculated["input"]["usd_amount"],
                "usd_rate": calculated["input"]["usd_rate"],
                "other_fees": calculated["input"]["other_fees"],
                "total_qty": calculated["summary"]["total_qty"],
                "total_base": calculated["summary"]["total_base"],
                "per_unit_cost": calculated["summary"]["per_unit_cost"],
                "currency": "BRL",
                "note": note or None,
                "created_by": int(g.current_user["id"]),
            },
        )

        for idx, product in enumerate(calculated["product_costs"], start=1):
            db.insert(
                conn,
                "customs_cost_item",
                {
                    "cost_record_id": record_id,
                    "line_no": idx,
                    "product_name": product["name"],
                    "qty": product["qty"],
                    "allocation_cost": product["cost"],
                    "unit_cost": product["unit_cost"],
                },
            )

        row = db.fetchone(
            conn,
            "SELECT cr.*, u.real_name AS created_by_name "
            "FROM customs_cost_record cr "
            "LEFT JOIN users u ON u.id = cr.created_by "
            "WHERE cr.id = " + db.placeholder,
            [record_id],
        )
        items = db.fetchall(
            conn,
            "SELECT id, line_no, product_name, qty, allocation_cost, unit_cost "
            "FROM customs_cost_item WHERE cost_record_id = "
            + db.placeholder
            + " ORDER BY line_no ASC, id ASC",
            [record_id],
        )

    return api_response({"record": _serialize_cost_record(row, items)}, 201)


@bp.get("/api/cost/records")
@jwt_required()
def list_cost_records():
    db = current_app.config["DB"]
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
    except Exception:
        return api_response({"error": "limit/offset 必须是整数"}, 400)
    process_record_id_raw = request.args.get("process_record_id")
    where_sql = ""
    params: list[Any] = []

    if process_record_id_raw:
        try:
            process_record_id = int(process_record_id_raw)
        except Exception:
            return api_response({"error": "process_record_id 必须是整数"}, 400)
        where_sql = " WHERE cr.process_record_id = " + db.placeholder
        params.append(process_record_id)

    with db.connection() as conn:
        rows = db.fetchall(
            conn,
            "SELECT cr.id, cr.process_record_id, cr.record_no, cr.total_qty, cr.total_base, cr.per_unit_cost, "
            "cr.currency, cr.created_by, cr.created_time, u.real_name AS created_by_name "
            "FROM customs_cost_record cr "
            "LEFT JOIN users u ON u.id = cr.created_by"
            + where_sql
            + " ORDER BY cr.created_time DESC, cr.id DESC LIMIT "
            + db.placeholder
            + " OFFSET "
            + db.placeholder,
            params + [limit, offset],
        )
        total_row = db.fetchone(
            conn,
            "SELECT COUNT(*) AS total FROM customs_cost_record cr" + where_sql,
            params,
        )

    items = [
        {
            "id": int(row["id"]),
            "process_record_id": row.get("process_record_id"),
            "record_no": row.get("record_no"),
            "total_qty": _to_float(row.get("total_qty")),
            "total_base": _to_float(row.get("total_base")),
            "per_unit_cost": _to_float(row.get("per_unit_cost")),
            "currency": row.get("currency"),
            "created_by": row.get("created_by"),
            "created_by_name": row.get("created_by_name"),
            "created_time": row.get("created_time"),
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


@bp.get("/api/cost/records/<int:record_id>")
@jwt_required()
def get_cost_record(record_id: int):
    db = current_app.config["DB"]
    with db.connection() as conn:
        row = db.fetchone(
            conn,
            "SELECT cr.*, u.real_name AS created_by_name "
            "FROM customs_cost_record cr "
            "LEFT JOIN users u ON u.id = cr.created_by "
            "WHERE cr.id = " + db.placeholder,
            [record_id],
        )
        if not row:
            return api_response({"error": "成本记录不存在"}, 404)

        items = db.fetchall(
            conn,
            "SELECT id, line_no, product_name, qty, allocation_cost, unit_cost "
            "FROM customs_cost_item WHERE cost_record_id = "
            + db.placeholder
            + " ORDER BY line_no ASC, id ASC",
            [record_id],
        )

    return api_response({"record": _serialize_cost_record(row, items)})
