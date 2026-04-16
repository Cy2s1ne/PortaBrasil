from datetime import datetime
from typing import Any

from flask import Blueprint, current_app, g, request

from app.core.auth import get_user_with_roles_by_id, hash_password_sha256, jwt_required, public_user
from app.core.responses import api_response

bp = Blueprint("admin_api", __name__)

MANAGEABLE_ROLES = {"SUPER_ADMIN", "ADMIN"}


def _is_super_admin(user: dict[str, Any]) -> bool:
    return "SUPER_ADMIN" in set(user.get("roles") or [])


def _parse_role_codes(payload: dict[str, Any]) -> list[str]:
    role_codes_raw = payload.get("role_codes") or payload.get("roles") or []
    if isinstance(role_codes_raw, str):
        role_codes = [code.strip() for code in role_codes_raw.split(",") if code.strip()]
    elif isinstance(role_codes_raw, list):
        role_codes = [str(code).strip() for code in role_codes_raw if str(code).strip()]
    else:
        role_codes = []
    return sorted({code.upper() for code in role_codes})


def _normalize_user_from_row(row: dict[str, Any]) -> dict[str, Any]:
    role_codes_raw = row.get("role_codes")
    roles: list[str] = []
    if role_codes_raw:
        roles = sorted({code.strip() for code in str(role_codes_raw).split(",") if code and code.strip()})
    return {
        "id": int(row["id"]),
        "username": row.get("username"),
        "real_name": row.get("real_name"),
        "phone": row.get("phone"),
        "email": row.get("email"),
        "status": int(row.get("status") or 0),
        "roles": roles,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def _validate_manage_permission(operator: dict[str, Any], target_user: dict[str, Any]) -> tuple[bool, Any]:
    if _is_super_admin(operator):
        return True, None
    if "SUPER_ADMIN" in set(target_user.get("roles") or []):
        return False, api_response({"error": "不能操作超级管理员账号"}, 403)
    return True, None


def _fetch_roles_by_codes(db, conn, role_codes: list[str]) -> list[dict[str, Any]]:
    placeholders = ", ".join([db.placeholder] * len(role_codes))
    return db.fetchall(
        conn,
        f"SELECT id, role_name, role_code, description FROM roles WHERE role_code IN ({placeholders})",
        role_codes,
    )


@bp.get("/api/admin/roles")
@jwt_required("SUPER_ADMIN", "ADMIN")
def list_roles():
    db = current_app.config["DB"]
    operator = g.current_user
    is_super = _is_super_admin(operator)
    with db.connection() as conn:
        if is_super:
            rows = db.fetchall(conn, "SELECT id, role_name, role_code, description FROM roles ORDER BY id ASC")
        else:
            rows = db.fetchall(
                conn,
                "SELECT id, role_name, role_code, description FROM roles WHERE role_code != "
                + db.placeholder
                + " ORDER BY id ASC",
                ["SUPER_ADMIN"],
            )
    items = [{**row, "id": int(row["id"])} for row in rows]
    return api_response({"items": items, "total": len(items)})


@bp.get("/api/admin/users")
@jwt_required("SUPER_ADMIN", "ADMIN")
def list_users():
    db = current_app.config["DB"]
    operator = g.current_user
    is_super = _is_super_admin(operator)

    try:
        limit = min(max(int(request.args.get("limit", 20)), 1), 100)
    except Exception:
        return api_response({"error": "limit 必须是整数"}, 400)

    try:
        offset = max(int(request.args.get("offset", 0)), 0)
    except Exception:
        return api_response({"error": "offset 必须是整数"}, 400)
    q = (request.args.get("q") or "").strip()
    role_code = (request.args.get("role_code") or "").strip().upper()
    status_raw = request.args.get("status")

    where_clauses: list[str] = []
    params: list[Any] = []

    if q:
        like = f"%{q}%"
        where_clauses.append(
            "(u.username LIKE "
            + db.placeholder
            + " OR u.real_name LIKE "
            + db.placeholder
            + " OR u.email LIKE "
            + db.placeholder
            + " OR u.phone LIKE "
            + db.placeholder
            + ")"
        )
        params.extend([like, like, like, like])

    if status_raw is not None and str(status_raw).strip() != "":
        try:
            status = int(status_raw)
        except Exception:
            return api_response({"error": "status 必须是 0 或 1"}, 400)
        if status not in (0, 1):
            return api_response({"error": "status 必须是 0 或 1"}, 400)
        where_clauses.append("u.status = " + db.placeholder)
        params.append(status)

    if role_code:
        where_clauses.append(
            "EXISTS (SELECT 1 FROM user_role ur2 JOIN roles r2 ON r2.id = ur2.role_id "
            "WHERE ur2.user_id = u.id AND r2.role_code = "
            + db.placeholder
            + ")"
        )
        params.append(role_code)

    if not is_super:
        where_clauses.append(
            "NOT EXISTS (SELECT 1 FROM user_role ur3 JOIN roles r3 ON r3.id = ur3.role_id "
            "WHERE ur3.user_id = u.id AND r3.role_code = "
            + db.placeholder
            + ")"
        )
        params.append("SUPER_ADMIN")

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    with db.connection() as conn:
        rows = db.fetchall(
            conn,
            "SELECT u.id, u.username, u.real_name, u.phone, u.email, u.status, u.created_at, u.updated_at, "
            "GROUP_CONCAT(DISTINCT r.role_code) AS role_codes "
            "FROM users u "
            "LEFT JOIN user_role ur ON ur.user_id = u.id "
            "LEFT JOIN roles r ON r.id = ur.role_id "
            + where_sql
            + " GROUP BY u.id ORDER BY u.created_at DESC, u.id DESC LIMIT "
            + db.placeholder
            + " OFFSET "
            + db.placeholder,
            params + [limit, offset],
        )
        total_row = db.fetchone(conn, "SELECT COUNT(*) AS total FROM users u " + where_sql, params)

    items = [_normalize_user_from_row(row) for row in rows]
    total = int(total_row["total"] if total_row else 0)
    return api_response({"items": items, "total": total, "limit": limit, "offset": offset})


@bp.post("/api/admin/users")
@jwt_required("SUPER_ADMIN", "ADMIN")
def create_user():
    payload = request.get_json(silent=True) or {}
    operator = g.current_user
    is_super = _is_super_admin(operator)

    username = str(payload.get("username") or "").strip()
    raw_password = str(payload.get("password") or "")
    real_name = str(payload.get("real_name") or "").strip() or None
    phone = str(payload.get("phone") or "").strip() or None
    email = str(payload.get("email") or "").strip() or None
    role_codes = _parse_role_codes(payload)

    try:
        status = int(payload.get("status", 1))
    except Exception:
        return api_response({"error": "status 必须是 0 或 1"}, 400)
    if status not in (0, 1):
        return api_response({"error": "status 必须是 0 或 1"}, 400)

    if not username or not raw_password:
        return api_response({"error": "username 和 password 必填"}, 400)
    if len(raw_password) < 6:
        return api_response({"error": "password 长度不能少于 6 位"}, 400)
    if not role_codes:
        return api_response({"error": "至少分配一个角色 role_codes"}, 400)
    if not is_super and "SUPER_ADMIN" in role_codes:
        return api_response({"error": "当前账号不能分配超级管理员角色"}, 403)

    db = current_app.config["DB"]
    with db.connection() as conn:
        existed = db.fetchone(conn, "SELECT id FROM users WHERE username = " + db.placeholder, [username])
        if existed:
            return api_response({"error": "用户名已存在"}, 409)

        if email:
            existed_email = db.fetchone(conn, "SELECT id FROM users WHERE email = " + db.placeholder, [email])
            if existed_email:
                return api_response({"error": "邮箱已存在"}, 409)

        role_rows = _fetch_roles_by_codes(db, conn, role_codes)
        found_codes = {str(item["role_code"]) for item in role_rows}
        missing_codes = [code for code in role_codes if code not in found_codes]
        if missing_codes:
            return api_response({"error": "存在无效角色", "missing_roles": missing_codes}, 400)

        user_id = db.insert(
            conn,
            "users",
            {
                "username": username,
                "password": hash_password_sha256(raw_password),
                "real_name": real_name,
                "phone": phone,
                "email": email,
                "status": status,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        )

        for role in role_rows:
            db.insert(conn, "user_role", {"user_id": user_id, "role_id": int(role["id"])})

        created_user = get_user_with_roles_by_id(db, conn, user_id)

    return api_response({"user": public_user(created_user)}, 201)


@bp.put("/api/admin/users/<int:user_id>")
@jwt_required("SUPER_ADMIN", "ADMIN")
def update_user(user_id: int):
    payload = request.get_json(silent=True) or {}
    operator = g.current_user
    is_super = _is_super_admin(operator)
    db = current_app.config["DB"]

    with db.connection() as conn:
        target_user = get_user_with_roles_by_id(db, conn, user_id)
        if not target_user:
            return api_response({"error": "用户不存在"}, 404)

        allowed, error_response = _validate_manage_permission(operator, target_user)
        if not allowed:
            return error_response

        update_data: dict[str, Any] = {}

        if "username" in payload:
            username = str(payload.get("username") or "").strip()
            if not username:
                return api_response({"error": "username 不能为空"}, 400)
            existed = db.fetchone(
                conn,
                "SELECT id FROM users WHERE username = " + db.placeholder + " AND id != " + db.placeholder,
                [username, user_id],
            )
            if existed:
                return api_response({"error": "用户名已存在"}, 409)
            update_data["username"] = username

        if "real_name" in payload:
            update_data["real_name"] = str(payload.get("real_name") or "").strip() or None
        if "phone" in payload:
            update_data["phone"] = str(payload.get("phone") or "").strip() or None
        if "email" in payload:
            email = str(payload.get("email") or "").strip() or None
            if email:
                existed_email = db.fetchone(
                    conn,
                    "SELECT id FROM users WHERE email = " + db.placeholder + " AND id != " + db.placeholder,
                    [email, user_id],
                )
                if existed_email:
                    return api_response({"error": "邮箱已存在"}, 409)
            update_data["email"] = email

        if "status" in payload:
            try:
                status = int(payload.get("status"))
            except Exception:
                return api_response({"error": "status 必须是 0 或 1"}, 400)
            if status not in (0, 1):
                return api_response({"error": "status 必须是 0 或 1"}, 400)
            if int(operator["id"]) == user_id and status == 0:
                return api_response({"error": "不能禁用当前登录账号"}, 400)
            update_data["status"] = status

        if "role_codes" in payload or "roles" in payload:
            role_codes = _parse_role_codes(payload)
            if not role_codes:
                return api_response({"error": "至少分配一个角色 role_codes"}, 400)
            if not is_super and "SUPER_ADMIN" in role_codes:
                return api_response({"error": "当前账号不能分配超级管理员角色"}, 403)
            if int(operator["id"]) == user_id and set(role_codes).isdisjoint(MANAGEABLE_ROLES):
                return api_response({"error": "当前登录账号至少保留一个管理角色"}, 400)

            role_rows = _fetch_roles_by_codes(db, conn, role_codes)
            found_codes = {str(item["role_code"]) for item in role_rows}
            missing_codes = [code for code in role_codes if code not in found_codes]
            if missing_codes:
                return api_response({"error": "存在无效角色", "missing_roles": missing_codes}, 400)

            db.execute(conn, "DELETE FROM user_role WHERE user_id = " + db.placeholder, [user_id])
            for role in role_rows:
                db.insert(conn, "user_role", {"user_id": user_id, "role_id": int(role["id"])})

        if not update_data and ("role_codes" not in payload and "roles" not in payload):
            return api_response({"error": "没有可更新字段"}, 400)

        if update_data:
            update_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.update_by_id(conn, "users", user_id, update_data)

        updated_user = get_user_with_roles_by_id(db, conn, user_id)
    return api_response({"user": public_user(updated_user)})


@bp.put("/api/admin/users/<int:user_id>/status")
@jwt_required("SUPER_ADMIN", "ADMIN")
def update_user_status(user_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        status = int(payload.get("status"))
    except Exception:
        return api_response({"error": "status 必须是 0 或 1"}, 400)
    if status not in (0, 1):
        return api_response({"error": "status 必须是 0 或 1"}, 400)

    operator = g.current_user
    db = current_app.config["DB"]
    with db.connection() as conn:
        target_user = get_user_with_roles_by_id(db, conn, user_id)
        if not target_user:
            return api_response({"error": "用户不存在"}, 404)

        allowed, error_response = _validate_manage_permission(operator, target_user)
        if not allowed:
            return error_response

        if int(operator["id"]) == user_id and status == 0:
            return api_response({"error": "不能禁用当前登录账号"}, 400)

        db.update_by_id(
            conn,
            "users",
            user_id,
            {"status": status, "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        )
        updated_user = get_user_with_roles_by_id(db, conn, user_id)

    return api_response({"user": public_user(updated_user)})


@bp.put("/api/admin/users/<int:user_id>/password")
@jwt_required("SUPER_ADMIN", "ADMIN")
def reset_user_password(user_id: int):
    payload = request.get_json(silent=True) or {}
    new_password = str(payload.get("new_password") or "")
    if len(new_password) < 6:
        return api_response({"error": "new_password 长度不能少于 6 位"}, 400)

    operator = g.current_user
    db = current_app.config["DB"]
    with db.connection() as conn:
        target_user = get_user_with_roles_by_id(db, conn, user_id)
        if not target_user:
            return api_response({"error": "用户不存在"}, 404)

        allowed, error_response = _validate_manage_permission(operator, target_user)
        if not allowed:
            return error_response

        db.update_by_id(
            conn,
            "users",
            user_id,
            {
                "password": hash_password_sha256(new_password),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        )

    return api_response({"message": "密码重置成功"})
