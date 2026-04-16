from flask import Blueprint, current_app, request

from app.core.auth import jwt_required
from app.core.responses import api_response
from services import upsert_business_with_fees

bp = Blueprint("documents_api", __name__)


@bp.post("/api/documents/from-text")
@jwt_required("SUPER_ADMIN", "ADMIN", "CUSTOMS")
def create_document_from_text():
    payload = request.get_json(silent=True) or {}
    raw_text = payload.get("raw_text") or payload.get("content") or payload.get("text")
    if not raw_text:
        return api_response({"error": "请求体需要 raw_text/content/text"}, 400)

    source_file_id = payload.get("file_id")
    source_page_no = payload.get("source_page_no")
    db = current_app.config["DB"]
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
