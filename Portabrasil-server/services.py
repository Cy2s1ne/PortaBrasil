import hashlib
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from sql.database import Database
from parser_rules import parse_demonstrativo_text
from pdf_parser import PDFParser


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))


BUSINESS_COLUMNS = {
    "s_ref",
    "n_ref",
    "document_no",
    "invoice_no",
    "nf_no",
    "process_no",
    "business_type",
    "trade_company",
    "customer_name",
    "customer_address",
    "customer_city",
    "customer_state",
    "customer_zip_code",
    "customer_tax_no",
    "issuer_name",
    "issuer_tax_no",
    "mawb_mbl",
    "hawb_hbl",
    "di_duimp_due",
    "registration_date",
    "arrival_date",
    "customs_clearance_date",
    "loading_date",
    "destination",
    "vessel_flight_name",
    "gross_weight",
    "volume_count",
    "cargo_desc",
    "freight_currency",
    "freight_amount",
    "fob_currency",
    "fob_amount",
    "cif_currency",
    "cif_amount",
    "cif_brl_amount",
    "dollar_rate",
    "euro_rate",
    "total_credit",
    "total_debit",
    "balance_amount",
    "balance_direction",
    "source_file_id",
    "source_page_no",
    "data_status",
}


FEE_COLUMNS = {
    "business_id",
    "fee_date",
    "fee_code",
    "fee_name",
    "credit_amount",
    "debit_amount",
    "line_no",
    "raw_text",
}


def now_string() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def try_count_pdf_pages(path: Path) -> int | None:
    try:
        from pypdf import PdfReader

        return len(PdfReader(str(path)).pages)
    except Exception:
        return None


def ensure_upload_dir() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(file_storage) -> tuple[Path, int, str]:
    ensure_upload_dir()
    original_name = Path(file_storage.filename or "upload.pdf").name
    suffix = Path(original_name).suffix.lower() or ".pdf"
    day_dir = UPLOAD_DIR / datetime.now().strftime("%Y%m%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    target_path = day_dir / f"{uuid.uuid4().hex}{suffix}"
    file_storage.save(target_path)
    return target_path, target_path.stat().st_size, sha256_file(target_path)


def create_or_get_pdf_file(db: Database, conn, *, file_name: str, file_path: Path, file_size: int, file_hash: str) -> tuple[dict[str, Any], bool]:
    existing = db.fetchone(conn, "SELECT * FROM pdf_file WHERE file_hash = " + db.placeholder, [file_hash])
    if existing:
        return existing, True

    file_id = db.insert(
        conn,
        "pdf_file",
        {
            "file_name": file_name,
            "file_path": str(file_path),
            "file_size": file_size,
            "file_hash": file_hash,
            "page_count": try_count_pdf_pages(file_path),
            "parse_status": "PENDING",
        },
    )
    row = db.fetchone(conn, "SELECT * FROM pdf_file WHERE id = " + db.placeholder, [file_id])
    return row, False


def create_parse_task(db: Database, conn, file_id: int, parser_type: str = "LLM") -> dict[str, Any]:
    task_id = db.insert(
        conn,
        "pdf_parse_task",
        {
            "file_id": file_id,
            "task_no": uuid.uuid4().hex,
            "parser_type": parser_type,
            "status": "PROCESSING",
            "start_time": now_string(),
        },
    )
    db.update_by_id(conn, "pdf_file", file_id, {"parse_status": "PROCESSING"})
    return db.fetchone(conn, "SELECT * FROM pdf_parse_task WHERE id = " + db.placeholder, [task_id])


def complete_parse_task(db: Database, conn, task_id: int, raw_result: dict[str, Any] | str, status: str = "SUCCESS", error: str | None = None) -> None:
    raw_text = raw_result if isinstance(raw_result, str) else json.dumps(raw_result, ensure_ascii=False, default=str)
    db.update_by_id(
        conn,
        "pdf_parse_task",
        task_id,
        {
            "status": status,
            "end_time": now_string(),
            "error_message": error,
            "raw_result": raw_text,
        },
    )


def upsert_business_with_fees(
    db: Database,
    conn,
    *,
    raw_text: str,
    source_file_id: int | None = None,
    source_page_no: int | None = None,
) -> dict[str, Any]:
    parsed = parse_demonstrativo_text(raw_text)
    business_data = {
        key: value
        for key, value in parsed.business.items()
        if key in BUSINESS_COLUMNS
    }
    business_data["source_file_id"] = source_file_id
    business_data["source_page_no"] = source_page_no
    business_data.setdefault("data_status", "DRAFT")

    existing = db.fetchone(conn, "SELECT id FROM customs_business WHERE s_ref = " + db.placeholder, [business_data["s_ref"]])
    if existing:
        business_id = int(existing["id"])
        db.update_by_id(conn, "customs_business", business_id, business_data)
        db.execute(conn, "DELETE FROM customs_business_fee_item WHERE business_id = " + db.placeholder, [business_id])
    else:
        business_id = db.insert(conn, "customs_business", business_data)

    for item in parsed.fee_items:
        fee_data = {key: value for key, value in item.items() if key in FEE_COLUMNS}
        fee_data["business_id"] = business_id
        db.insert(conn, "customs_business_fee_item", fee_data)

    business = db.fetchone(conn, "SELECT * FROM customs_business WHERE id = " + db.placeholder, [business_id])
    fees = db.fetchall(
        conn,
        "SELECT * FROM customs_business_fee_item WHERE business_id = " + db.placeholder + " ORDER BY line_no, id",
        [business_id],
    )
    business["fee_items"] = fees
    return business


def parse_file_and_store(db: Database, file_id: int) -> dict[str, Any]:
    with db.connection() as conn:
        pdf_file = db.fetchone(conn, "SELECT * FROM pdf_file WHERE id = " + db.placeholder, [file_id])
        if not pdf_file:
            raise ValueError(f"文件不存在: {file_id}")

        task = create_parse_task(db, conn, file_id)

    try:
        if not os.getenv("ZHIPU_API_KEY"):
            raise RuntimeError("ZHIPU_API_KEY 未配置，无法调用智谱 PDF 解析接口")

        parser = PDFParser()
        parser_result = parser.parse(pdf_file["file_path"])
        content = parser_result.get("content") or ""
        if not content.strip():
            raise RuntimeError("PDF 解析成功但 content 为空")

        with db.connection() as conn:
            business = upsert_business_with_fees(db, conn, raw_text=content, source_file_id=file_id)
            complete_parse_task(db, conn, int(task["id"]), parser_result)
            db.update_by_id(conn, "pdf_file", file_id, {"parse_status": "SUCCESS"})
            return {"file": db.fetchone(conn, "SELECT * FROM pdf_file WHERE id = " + db.placeholder, [file_id]), "task_id": task["id"], "business": business}
    except Exception as exc:
        with db.connection() as conn:
            complete_parse_task(db, conn, int(task["id"]), {"error": str(exc)}, status="FAILED", error=str(exc))
            db.update_by_id(conn, "pdf_file", file_id, {"parse_status": "FAILED", "remark": str(exc)[:500]})
        raise
