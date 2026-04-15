from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

from database import get_database
from services import (
    create_or_get_pdf_file,
    parse_file_and_store,
    save_upload,
    upsert_business_with_fees,
)

try:
    from flask_cors import CORS
except Exception:
    CORS = None


ALLOWED_EXTENSIONS = {"pdf"}


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


def is_truthy(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "y", "on"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

    if CORS:
        CORS(app, resources={r"/api/*": {"origins": "*"}})
    else:
        @app.after_request
        def add_cors_headers(response):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            return response

    db = get_database()
    db.initialize()

    @app.errorhandler(Exception)
    def handle_error(error):
        status = getattr(error, "code", 500)
        if status < 400:
            status = 500
        return api_response({"error": str(error)}, status)

    @app.get("/api/health")
    def health():
        return api_response({"status": "ok", "database": db.backend})

    @app.post("/api/files/upload")
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

    @app.post("/api/files/<int:file_id>/parse")
    def parse_existing_file(file_id: int):
        result = parse_file_and_store(db, file_id)
        return api_response(result)

    @app.get("/api/files")
    def list_files():
        limit = min(int(request.args.get("limit", 20)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
        status = request.args.get("status")
        params: list[Any] = []
        where = ""
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

    @app.get("/api/files/<int:file_id>")
    def get_file(file_id: int):
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

    @app.post("/api/documents/from-text")
    def create_document_from_text():
        payload = request.get_json(silent=True) or {}
        raw_text = payload.get("raw_text") or payload.get("content") or payload.get("text")
        if not raw_text:
            return api_response({"error": "请求体需要 raw_text/content/text"}, 400)

        source_file_id = payload.get("file_id")
        source_page_no = payload.get("source_page_no")
        with db.connection() as conn:
            if source_file_id:
                pdf_file = db.fetchone(conn, "SELECT id FROM pdf_file WHERE id = " + db.placeholder, [source_file_id])
                if not pdf_file:
                    return api_response({"error": "file_id 不存在"}, 404)
            business = upsert_business_with_fees(
                db,
                conn,
                raw_text=raw_text,
                source_file_id=source_file_id,
                source_page_no=source_page_no,
            )
            if source_file_id:
                db.update_by_id(conn, "pdf_file", int(source_file_id), {"parse_status": "SUCCESS"})
        return api_response({"business": business}, 201)

    @app.get("/api/business")
    def list_business():
        limit = min(int(request.args.get("limit", 20)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
        search = request.args.get("q")
        params: list[Any] = []
        where = ""
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

    @app.get("/api/business/<int:business_id>")
    def get_business(business_id: int):
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

    @app.get("/api/business/<int:business_id>/fees")
    def list_fees(business_id: int):
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

    @app.get("/api/tasks/<int:task_id>")
    def get_task(task_id: int):
        with db.connection() as conn:
            task = db.fetchone(conn, "SELECT * FROM pdf_parse_task WHERE id = " + db.placeholder, [task_id])
            if not task:
                return api_response({"error": "任务不存在"}, 404)
        return api_response({"task": task})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
