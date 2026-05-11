import hashlib
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from sql.database import Database
from parser_rules import parse_demonstrativo_text


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


STEP_NAMES = {
    1: "货物到港确认",
    2: "海关申报",
    3: "文件审核",
    4: "税费计算",
    5: "税费缴纳",
    6: "海关查验",
    7: "放行通知",
    8: "提货准备",
    9: "货物提取",
    10: "运输配送",
}


def now_string() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _date_to_step_time(value: Any) -> str | None:
    if not value:
        return None
    raw = str(value)
    if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
        return raw[5:10]
    return raw[:20]


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
    sync_process_record_for_business(db, conn, business, fees)
    return business


def _business_bl_no(business: dict[str, Any]) -> str:
    for key in ("mawb_mbl", "hawb_hbl", "di_duimp_due", "process_no", "s_ref"):
        value = str(business.get(key) or "").strip()
        if value:
            return value[:64]
    return f"BUS-{business.get('id')}"


def _derive_step_statuses(business: dict[str, Any], fee_items: list[dict[str, Any]]) -> dict[int, tuple[str, str | None]]:
    completed_until = 0

    if business.get("arrival_date"):
        completed_until = max(completed_until, 1)
    if business.get("registration_date") or business.get("di_duimp_due"):
        completed_until = max(completed_until, 2)
    if business.get("invoice_no") or business.get("nf_no") or business.get("document_no"):
        completed_until = max(completed_until, 3)
    if business.get("total_debit") is not None or business.get("cif_brl_amount") is not None or fee_items:
        completed_until = max(completed_until, 4)
    if business.get("balance_amount") is not None:
        completed_until = max(completed_until, 5)
    if business.get("customs_clearance_date"):
        completed_until = max(completed_until, 7)
    if business.get("loading_date"):
        completed_until = max(completed_until, 9)

    step_dates = {
        1: _date_to_step_time(business.get("arrival_date")),
        2: _date_to_step_time(business.get("registration_date")),
        3: _date_to_step_time(business.get("registration_date")),
        4: _date_to_step_time(business.get("registration_date")),
        5: _date_to_step_time(business.get("registration_date")),
        6: _date_to_step_time(business.get("customs_clearance_date")),
        7: _date_to_step_time(business.get("customs_clearance_date")),
        8: _date_to_step_time(business.get("loading_date")),
        9: _date_to_step_time(business.get("loading_date")),
        10: None,
    }
    return {
        step_no: ("COMPLETE" if step_no <= completed_until else "PENDING", step_dates.get(step_no))
        for step_no in range(1, 11)
    }


def _derive_overall_status_from_steps(step_statuses: dict[int, tuple[str, str | None]]) -> str:
    complete_count = sum(1 for status, _date in step_statuses.values() if status == "COMPLETE")
    if complete_count >= 10:
        return "CLEARED"
    if step_statuses.get(6, ("PENDING", None))[0] == "COMPLETE":
        return "INSPECTION"
    return "PROCESSING"


def sync_process_record_for_business(
    db: Database,
    conn,
    business: dict[str, Any],
    fee_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    business_id = business.get("id")
    if not business_id:
        return None

    fee_items = fee_items or []
    bl_no = _business_bl_no(business)
    step_statuses = _derive_step_statuses(business, fee_items)
    overall_status = _derive_overall_status_from_steps(step_statuses)
    record_data = {
        "business_id": int(business_id),
        "bl_no": bl_no,
        "goods_desc": business.get("cargo_desc") or business.get("customer_name") or business.get("s_ref"),
        "declaration_date": business.get("registration_date") or business.get("arrival_date"),
        "port_name": business.get("destination") or business.get("customer_city") or business.get("customer_state"),
        "overall_status": overall_status,
        "updated_time": now_string(),
    }

    existing = db.fetchone(
        conn,
        "SELECT id FROM customs_process_record WHERE business_id = " + db.placeholder,
        [int(business_id)],
    )
    if not existing:
        existing = db.fetchone(
            conn,
            "SELECT id FROM customs_process_record WHERE bl_no = " + db.placeholder,
            [bl_no],
        )

    if existing:
        process_id = int(existing["id"])
        db.update_by_id(conn, "customs_process_record", process_id, record_data)
    else:
        record_data["created_time"] = now_string()
        process_id = db.insert(conn, "customs_process_record", record_data)

    for step_no in range(1, 11):
        status, completion_time = step_statuses[step_no]
        existing_step = db.fetchone(
            conn,
            "SELECT id FROM customs_process_step WHERE process_id = "
            + db.placeholder
            + " AND step_no = "
            + db.placeholder,
            [process_id, step_no],
        )
        step_data = {
            "status": status,
            "completion_time": completion_time,
            "step_desc": f"{bl_no} - {STEP_NAMES[step_no]}",
            "updated_time": now_string(),
        }
        if existing_step:
            db.update_by_id(conn, "customs_process_step", int(existing_step["id"]), step_data)
        else:
            step_data.update({"process_id": process_id, "step_no": step_no, "created_time": now_string()})
            db.insert(conn, "customs_process_step", step_data)

    return db.fetchone(conn, "SELECT * FROM customs_process_record WHERE id = " + db.placeholder, [process_id])


def sync_missing_process_records(db: Database, conn, limit: int = 500) -> int:
    rows = db.fetchall(
        conn,
        "SELECT b.* FROM customs_business b "
        "LEFT JOIN customs_process_record p ON p.business_id = b.id "
        "WHERE p.id IS NULL "
        "ORDER BY b.updated_time DESC, b.id DESC LIMIT "
        + db.placeholder,
        [limit],
    )
    synced = 0
    for business in rows:
        fees = db.fetchall(
            conn,
            "SELECT * FROM customs_business_fee_item WHERE business_id = "
            + db.placeholder
            + " ORDER BY line_no, id",
            [business["id"]],
        )
        if sync_process_record_for_business(db, conn, business, fees):
            synced += 1
    return synced


def parse_file_and_store(
    db: Database,
    file_id: int,
    *,
    created_by: int | None = None,
    auto_audit: bool = True,
) -> dict[str, Any]:
    with db.connection() as conn:
        pdf_file = db.fetchone(conn, "SELECT * FROM pdf_file WHERE id = " + db.placeholder, [file_id])
        if not pdf_file:
            raise ValueError(f"文件不存在: {file_id}")

        task = create_parse_task(db, conn, file_id, parser_type="LANGCHAIN_AGENT")

    try:
        from app.agents.pdf_agent import run_pdf_ingestion_agent

        result = run_pdf_ingestion_agent(
            db=db,
            pdf_file=pdf_file,
            task=task,
            created_by=created_by,
            auto_audit=auto_audit,
        )

        with db.connection() as conn:
            task_raw_result = result.pop("task_raw_result", result)
            complete_parse_task(db, conn, int(task["id"]), task_raw_result)
            db.update_by_id(conn, "pdf_file", file_id, {"parse_status": "SUCCESS"})
            result["file"] = db.fetchone(conn, "SELECT * FROM pdf_file WHERE id = " + db.placeholder, [file_id])

        return result
    except Exception as exc:
        with db.connection() as conn:
            complete_parse_task(db, conn, int(task["id"]), {"error": str(exc)}, status="FAILED", error=str(exc))
            db.update_by_id(conn, "pdf_file", file_id, {"parse_status": "FAILED", "remark": str(exc)[:500]})
        raise
