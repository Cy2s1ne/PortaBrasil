from flask import Blueprint, current_app, g, request

from app.core.auth import (
    create_access_token,
    get_role_by_code,
    get_user_with_roles_by_id,
    get_user_with_roles_by_identity,
    hash_password_sha256,
    jwt_required,
    public_user,
    verify_password,
)
from app.core.responses import api_response

bp = Blueprint("auth_api", __name__)


@bp.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    identity = (payload.get("username") or payload.get("email") or payload.get("account") or "").strip()
    password = payload.get("password") or ""
    if not identity or not password:
        return api_response({"error": "请求体需要 username/email 和 password"}, 400)

    db = current_app.config["DB"]
    with db.connection() as conn:
        user = get_user_with_roles_by_identity(db, conn, identity)
        if not user:
            return api_response({"error": "账号或密码错误"}, 401)

        if int(user.get("status", 0) or 0) != 1:
            return api_response({"error": "用户已被禁用"}, 403)

        verified, needs_upgrade = verify_password(password, str(user.get("password") or ""))
        if not verified:
            return api_response({"error": "账号或密码错误"}, 401)

        if needs_upgrade:
            db.update_by_id(conn, "users", int(user["id"]), {"password": hash_password_sha256(password)})
            user["password"] = hash_password_sha256(password)

    token, expires_in = create_access_token(user)
    return api_response(
        {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "user": public_user(user),
        }
    )


@bp.post("/api/auth/register")
def register():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username") or "").strip()
    raw_password = str(payload.get("password") or "")
    real_name = payload.get("real_name")
    phone = payload.get("phone")
    email = payload.get("email")

    if not username or not raw_password:
        return api_response({"error": "username 和 password 必填"}, 400)

    db = current_app.config["DB"]
    default_register_role = current_app.config["DEFAULT_REGISTER_ROLE"]
    with db.connection() as conn:
        existed = db.fetchone(conn, "SELECT id FROM users WHERE username = " + db.placeholder, [username])
        if existed:
            return api_response({"error": "用户名已存在"}, 409)

        if email:
            existed_email = db.fetchone(conn, "SELECT id FROM users WHERE email = " + db.placeholder, [email])
            if existed_email:
                return api_response({"error": "邮箱已存在"}, 409)

        role = get_role_by_code(db, conn, default_register_role)
        if not role:
            return api_response({"error": f"系统缺少默认注册角色: {default_register_role}"}, 500)

        user_id = db.insert(
            conn,
            "users",
            {
                "username": username,
                "password": hash_password_sha256(raw_password),
                "real_name": real_name,
                "phone": phone,
                "email": email,
                "status": 1,
            },
        )
        db.insert(
            conn,
            "user_role",
            {
                "user_id": user_id,
                "role_id": int(role["id"]),
            },
        )
        user = get_user_with_roles_by_id(db, conn, user_id)

    token, expires_in = create_access_token(user)
    return api_response(
        {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "user": public_user(user),
        },
        201,
    )


@bp.post("/api/auth/forgot-password")
def forgot_password():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username") or "").strip()
    email = str(payload.get("email") or "").strip()
    new_password = str(payload.get("new_password") or "")

    if not username or not email or not new_password:
        return api_response({"error": "username、email、new_password 必填"}, 400)
    if len(new_password) < 6:
        return api_response({"error": "新密码长度不能少于 6 位"}, 400)

    db = current_app.config["DB"]
    with db.connection() as conn:
        user = db.fetchone(
            conn,
            "SELECT id, email FROM users WHERE username = " + db.placeholder,
            [username],
        )
        if not user:
            return api_response({"error": "用户不存在"}, 404)

        stored_email = str(user.get("email") or "").strip().lower()
        if stored_email != email.lower():
            return api_response({"error": "用户名与邮箱不匹配"}, 400)

        db.update_by_id(
            conn,
            "users",
            int(user["id"]),
            {"password": hash_password_sha256(new_password)},
        )

    return api_response({"message": "密码重置成功，请使用新密码登录"})


@bp.get("/api/auth/me")
@jwt_required()
def get_current_user():
    return api_response({"user": g.current_user})


@bp.post("/api/auth/users")
@jwt_required("SUPER_ADMIN", "ADMIN")
def create_user():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username") or "").strip()
    raw_password = str(payload.get("password") or "")
    real_name = payload.get("real_name")
    phone = payload.get("phone")
    email = payload.get("email")
    try:
        status = int(payload.get("status", 1))
    except Exception:
        return api_response({"error": "status 必须是 0 或 1"}, 400)

    role_codes_raw = payload.get("role_codes") or payload.get("roles") or []
    if isinstance(role_codes_raw, str):
        role_codes = [code.strip() for code in role_codes_raw.split(",") if code.strip()]
    elif isinstance(role_codes_raw, list):
        role_codes = [str(code).strip() for code in role_codes_raw if str(code).strip()]
    else:
        role_codes = []
    role_codes = sorted({code.upper() for code in role_codes})

    if not username or not raw_password:
        return api_response({"error": "username 和 password 必填"}, 400)
    if not role_codes:
        return api_response({"error": "至少分配一个角色 role_codes"}, 400)

    db = current_app.config["DB"]
    with db.connection() as conn:
        existed = db.fetchone(conn, "SELECT id FROM users WHERE username = " + db.placeholder, [username])
        if existed:
            return api_response({"error": "用户名已存在"}, 409)

        placeholders = ", ".join([db.placeholder] * len(role_codes))
        role_rows = db.fetchall(
            conn,
            f"SELECT id, role_code FROM roles WHERE role_code IN ({placeholders})",
            role_codes,
        )
        found_codes = {str(row["role_code"]) for row in role_rows}
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
                "status": 1 if status == 1 else 0,
            },
        )

        for role in role_rows:
            db.insert(
                conn,
                "user_role",
                {
                    "user_id": user_id,
                    "role_id": int(role["id"]),
                },
            )

        created_user = get_user_with_roles_by_id(db, conn, user_id)

    return api_response({"user": public_user(created_user)}, 201)
