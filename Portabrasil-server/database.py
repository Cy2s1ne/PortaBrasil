import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SQLITE_PATH = BASE_DIR / "instance" / "portabrasil.db"


SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS pdf_file (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_hash TEXT UNIQUE,
    page_count INTEGER,
    parse_status TEXT NOT NULL DEFAULT 'PENDING',
    upload_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    remark TEXT
);

CREATE INDEX IF NOT EXISTS idx_pdf_file_status ON pdf_file(parse_status);
CREATE INDEX IF NOT EXISTS idx_pdf_file_upload_time ON pdf_file(upload_time);

CREATE TABLE IF NOT EXISTS pdf_parse_task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    task_no TEXT NOT NULL UNIQUE,
    parser_type TEXT NOT NULL DEFAULT 'LLM',
    status TEXT NOT NULL DEFAULT 'PENDING',
    start_time TEXT,
    end_time TEXT,
    error_message TEXT,
    raw_result TEXT,
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(file_id) REFERENCES pdf_file(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_parse_task_file_id ON pdf_parse_task(file_id);
CREATE INDEX IF NOT EXISTS idx_parse_task_status ON pdf_parse_task(status);

CREATE TABLE IF NOT EXISTS customs_business (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    s_ref TEXT NOT NULL UNIQUE,
    n_ref TEXT,
    document_no TEXT,
    invoice_no TEXT,
    nf_no TEXT,
    process_no TEXT,
    business_type TEXT,
    trade_company TEXT,
    customer_name TEXT,
    customer_address TEXT,
    customer_city TEXT,
    customer_state TEXT,
    customer_zip_code TEXT,
    customer_tax_no TEXT,
    issuer_name TEXT,
    issuer_tax_no TEXT,
    mawb_mbl TEXT,
    hawb_hbl TEXT,
    di_duimp_due TEXT,
    registration_date TEXT,
    arrival_date TEXT,
    customs_clearance_date TEXT,
    loading_date TEXT,
    destination TEXT,
    vessel_flight_name TEXT,
    gross_weight TEXT,
    volume_count INTEGER,
    cargo_desc TEXT,
    freight_currency TEXT,
    freight_amount TEXT,
    fob_currency TEXT,
    fob_amount TEXT,
    cif_currency TEXT,
    cif_amount TEXT,
    cif_brl_amount TEXT,
    dollar_rate TEXT,
    euro_rate TEXT,
    total_credit TEXT,
    total_debit TEXT,
    balance_amount TEXT,
    balance_direction TEXT,
    source_file_id INTEGER,
    source_page_no INTEGER,
    data_status TEXT NOT NULL DEFAULT 'DRAFT',
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_file_id) REFERENCES pdf_file(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_business_n_ref ON customs_business(n_ref);
CREATE INDEX IF NOT EXISTS idx_business_invoice_no ON customs_business(invoice_no);
CREATE INDEX IF NOT EXISTS idx_business_nf_no ON customs_business(nf_no);
CREATE INDEX IF NOT EXISTS idx_business_customer_name ON customs_business(customer_name);
CREATE INDEX IF NOT EXISTS idx_business_source_file_id ON customs_business(source_file_id);

CREATE TABLE IF NOT EXISTS customs_business_fee_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    fee_date TEXT,
    fee_code TEXT,
    fee_name TEXT NOT NULL,
    credit_amount TEXT,
    debit_amount TEXT,
    line_no INTEGER,
    raw_text TEXT,
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(business_id) REFERENCES customs_business(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_fee_item_business_id ON customs_business_fee_item(business_id);
CREATE INDEX IF NOT EXISTS idx_fee_item_fee_code ON customs_business_fee_item(fee_code);
CREATE INDEX IF NOT EXISTS idx_fee_item_fee_date ON customs_business_fee_item(fee_date);
"""


class Database:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv("DATABASE_URL") or f"sqlite:///{DEFAULT_SQLITE_PATH}"
        self.backend = "mysql" if self.database_url.startswith(("mysql://", "mysql+pymysql://")) else "sqlite"
        self.placeholder = "%s" if self.backend == "mysql" else "?"

    def connect(self):
        if self.backend == "mysql":
            import pymysql
            from pymysql.cursors import DictCursor

            parsed = urlparse(self.database_url.replace("mysql+pymysql://", "mysql://", 1))
            query = parse_qs(parsed.query)
            charset = query.get("charset", ["utf8mb4"])[0]
            return pymysql.connect(
                host=parsed.hostname or "localhost",
                port=parsed.port or 3306,
                user=unquote(parsed.username or ""),
                password=unquote(parsed.password or ""),
                database=(parsed.path or "/").lstrip("/"),
                charset=charset,
                cursorclass=DictCursor,
                autocommit=False,
            )

        path = self.database_url.replace("sqlite:///", "", 1)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        if self.backend != "sqlite":
            return

        with self.connection() as conn:
            conn.executescript(SQLITE_SCHEMA)

    @contextmanager
    def connection(self):
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def normalize_params(self, values: list[Any] | tuple[Any, ...]) -> list[Any]:
        normalized = []
        for value in values:
            if isinstance(value, Decimal):
                normalized.append(str(value))
            elif isinstance(value, (datetime, date)):
                normalized.append(value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat())
            else:
                normalized.append(value)
        return normalized

    def execute(self, conn, sql: str, params: list[Any] | tuple[Any, ...] = ()):
        cursor = conn.cursor()
        cursor.execute(sql, self.normalize_params(params))
        return cursor

    def fetchone(self, conn, sql: str, params: list[Any] | tuple[Any, ...] = ()) -> dict[str, Any] | None:
        cursor = self.execute(conn, sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetchall(self, conn, sql: str, params: list[Any] | tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        cursor = self.execute(conn, sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def insert(self, conn, table: str, data: dict[str, Any]) -> int:
        columns = list(data.keys())
        placeholders = ", ".join([self.placeholder] * len(columns))
        column_sql = ", ".join(columns)
        values = [data[column] for column in columns]
        cursor = self.execute(conn, f"INSERT INTO {table} ({column_sql}) VALUES ({placeholders})", values)
        return int(cursor.lastrowid)

    def update_by_id(self, conn, table: str, row_id: int, data: dict[str, Any]) -> None:
        if not data:
            return

        assignments = ", ".join([f"{column} = {self.placeholder}" for column in data.keys()])
        values = list(data.values()) + [row_id]
        self.execute(conn, f"UPDATE {table} SET {assignments} WHERE id = {self.placeholder}", values)


def get_database() -> Database:
    return Database()
