import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any

import jwt
from flask import current_app, g, request
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.responses import api_response


def hash_password_sha256(raw_password: str) -> str:
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


def is_sha256_hex(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in value)


def verify_password(raw_password: str, stored_password: str) -> tuple[bool, bool]:
    hashed = hash_password_sha256(raw_password)
    if is_sha256_hex(stored_password):
        return secrets.compare_digest(stored_password.lower(), hashed), False

    # 向后兼容：如果库里是明文，登录成功后会升级为 sha256。
    if secrets.compare_digest(stored_password, raw_password):
        return True, True
    return False, False


def normalize_user_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None

    role_codes_raw = row.get("role_codes")
    roles = []
    if role_codes_raw:
        roles = [code.strip() for code in str(role_codes_raw).split(",") if code and code.strip()]

    user = dict(row)
    user["roles"] = sorted(set(roles))
    user.pop("role_codes", None)
    return user


def get_user_with_roles_by_identity(db, conn, identity: str) -> dict[str, Any] | None:
    sql = (
        "SELECT u.id, u.username, u.password, u.real_name, u.phone, u.email, u.status, u.created_at, u.updated_at, "
        "GROUP_CONCAT(DISTINCT r.role_code) AS role_codes "
        "FROM users u "
        "LEFT JOIN user_role ur ON ur.user_id = u.id "
        "LEFT JOIN roles r ON r.id = ur.role_id "
        "WHERE (u.username = "
        + db.placeholder
        + " OR u.email = "
        + db.placeholder
        + ") GROUP BY u.id"
    )
    row = db.fetchone(conn, sql, [identity, identity])
    return normalize_user_row(row)


def get_user_with_roles_by_id(db, conn, user_id: int) -> dict[str, Any] | None:
    sql = (
        "SELECT u.id, u.username, u.password, u.real_name, u.phone, u.email, u.status, u.created_at, u.updated_at, "
        "GROUP_CONCAT(DISTINCT r.role_code) AS role_codes "
        "FROM users u "
        "LEFT JOIN user_role ur ON ur.user_id = u.id "
        "LEFT JOIN roles r ON r.id = ur.role_id "
        "WHERE u.id = "
        + db.placeholder
        + " GROUP BY u.id"
    )
    row = db.fetchone(conn, sql, [user_id])
    return normalize_user_row(row)


def get_role_by_code(db, conn, role_code: str) -> dict[str, Any] | None:
    return db.fetchone(conn, "SELECT id, role_code FROM roles WHERE role_code = " + db.placeholder, [role_code])


def public_user(user: dict[str, Any]) -> dict[str, Any]:
    safe = dict(user)
    safe.pop("password", None)
    return safe


def create_access_token(user: dict[str, Any]) -> tuple[str, int]:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=int(current_app.config["JWT_EXPIRES_MINUTES"]))
    payload = {
        "sub": str(user["id"]),
        "username": user["username"],
        "roles": user.get("roles", []),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm=current_app.config["JWT_ALGORITHM"])
    return token, int((expire - now).total_seconds())


def jwt_required(*required_roles: str):
    role_set = set(required_roles)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return api_response({"error": "缺少或无效 Authorization Bearer Token"}, 401)

            token = auth_header[7:].strip()
            if not token:
                return api_response({"error": "Token 不能为空"}, 401)

            try:
                payload = jwt.decode(
                    token,
                    current_app.config["JWT_SECRET"],
                    algorithms=[current_app.config["JWT_ALGORITHM"]],
                )
            except ExpiredSignatureError:
                return api_response({"error": "Token 已过期"}, 401)
            except InvalidTokenError:
                return api_response({"error": "Token 无效"}, 401)

            user_id_raw = payload.get("sub")
            if not user_id_raw:
                return api_response({"error": "Token 缺少用户信息"}, 401)

            try:
                user_id = int(user_id_raw)
            except Exception:
                return api_response({"error": "Token 用户信息格式错误"}, 401)

            db = current_app.config["DB"]
            with db.connection() as conn:
                user = get_user_with_roles_by_id(db, conn, user_id)

            if not user:
                return api_response({"error": "用户不存在"}, 401)

            if int(user.get("status", 0) or 0) != 1:
                return api_response({"error": "用户已被禁用"}, 403)

            user_roles = set(user.get("roles", []))
            if role_set and user_roles.isdisjoint(role_set):
                return api_response(
                    {
                        "error": "权限不足",
                        "required_roles": sorted(role_set),
                        "current_roles": sorted(user_roles),
                    },
                    403,
                )

            g.current_user = public_user(user)
            g.jwt_payload = payload
            return func(*args, **kwargs)

        return wrapper

    return decorator
