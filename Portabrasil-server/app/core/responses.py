from datetime import date, datetime
from decimal import Decimal
from typing import Any

from flask import jsonify


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat()
    return value


def api_response(payload: Any = None, status: int = 200):
    return jsonify(json_safe(payload or {})), status
