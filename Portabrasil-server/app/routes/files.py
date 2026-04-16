from pathlib import Path
from typing import Any

from flask import Blueprint, current_app, request
from werkzeug.utils import secure_filename

from app.core.auth import jwt_required
from app.core.responses import api_response
from services import create_or_get_pdf_file, parse_file_and_store, save_upload

bp = Blueprint("files_api", __name__)

ALLOWED_EXTENSIONS = {"pdf"}


def is_truthy(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "y", "on"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.post("/api/files/upload")
@jwt_required("SUPER_ADMIN", "ADMIN", "CUSTOMS")
def upload_file():
    if "file" not in request.files:
        return api_response({"error": "缺少 multipart 字段 file"}, 400)

    file_storage = request.files["file"]
    if not file_storage.filename:
        return api_response({"error": "文件名为空"}, 400)

    original_name = secure_filename(file_storage.filename) or Path(file_storage.filename).name
    if not allowed_file(original_name):
        return api_response({"error": "当前只支持 PDF 文件"}, 400)

    saved_path, file_size, file_hash = save_upload(file_storage)
    parse_now = is_truthy(request.form.get("parse"), default=True)

    db = current_app.config["DB"]
    with db.connection() as conn:
        pdf_file, duplicated = create_or_get_pdf_file(
            db,
            conn,
            file_name=original_name,
            file_path=saved_path,
            file_size=file_size,
            file_hash=file_hash,
        )

    if duplicated and Path(saved_path).exists():
        Path(saved_path).unlink()

    if parse_now and pdf_file["parse_status"] != "SUCCESS":
        result = parse_file_and_store(db, int(pdf_file["id"]))
        return api_response({"duplicated": duplicated, **result}, 201 if not duplicated else 200)

    return api_response({"duplicated": duplicated, "file": pdf_file}, 201 if not duplicated else 200)


@bp.post("/api/files/<int:file_id>/parse")
@jwt_required("SUPER_ADMIN", "ADMIN", "CUSTOMS")
def parse_existing_file(file_id: int):
    db = current_app.config["DB"]
    result = parse_file_and_store(db, file_id)
    return api_response(result)


@bp.get("/api/files")
@jwt_required()
def list_files():
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = max(int(request.args.get("offset", 0)), 0)
    status = request.args.get("status")
    params: list[Any] = []
    where = ""
    db = current_app.config["DB"]
    if status:
        where = " WHERE parse_status = " + db.placeholder
        params.append(status)

    with db.connection() as conn:
        rows = db.fetchall(
            conn,
            f"SELECT * FROM pdf_file{where} ORDER BY upload_time DESC, id DESC LIMIT {db.placeholder} OFFSET {db.placeholder}",
            params + [limit, offset],
        )
        total = db.fetchone(conn, f"SELECT COUNT(*) AS total FROM pdf_file{where}", params)
    return api_response({"items": rows, "total": total["total"] if total else 0, "limit": limit, "offset": offset})


@bp.get("/api/files/<int:file_id>")
@jwt_required()
def get_file(file_id: int):
    db = current_app.config["DB"]
    with db.connection() as conn:
        pdf_file = db.fetchone(conn, "SELECT * FROM pdf_file WHERE id = " + db.placeholder, [file_id])
        if not pdf_file:
            return api_response({"error": "文件不存在"}, 404)
        tasks = db.fetchall(
            conn,
            "SELECT id, task_no, parser_type, status, start_time, end_time, error_message, created_time, updated_time "
            "FROM pdf_parse_task WHERE file_id = "
            + db.placeholder
            + " ORDER BY created_time DESC, id DESC",
            [file_id],
        )
        businesses = db.fetchall(
            conn,
            "SELECT * FROM customs_business WHERE source_file_id = " + db.placeholder + " ORDER BY id DESC",
            [file_id],
        )
    return api_response({"file": pdf_file, "tasks": tasks, "businesses": businesses})
