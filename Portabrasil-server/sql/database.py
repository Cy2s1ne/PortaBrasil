import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
import hashlib
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse


BASE_DIR = Path(__file__).resolve().parent.parent
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

CREATE TABLE IF NOT EXISTS statement_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    statement_no TEXT NOT NULL,
    issue_date TEXT,
    due_date TEXT,
    total_amount TEXT,
    amount_direction TEXT,
    customer_name TEXT,
    customer_address TEXT,
    customer_city TEXT,
    customer_state TEXT,
    customer_zip_code TEXT,
    customer_tax_no TEXT,
    issuer_name TEXT,
    source_file_id INTEGER,
    source_page_no INTEGER,
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_file_id) REFERENCES pdf_file(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_statement_summary_no ON statement_summary(statement_no);
CREATE INDEX IF NOT EXISTS idx_statement_summary_source ON statement_summary(source_file_id);

CREATE TABLE IF NOT EXISTS statement_summary_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary_id INTEGER NOT NULL,
    n_ref TEXT,
    s_ref TEXT,
    nf_no TEXT,
    amount_direction TEXT,
    balance_amount TEXT,
    business_id INTEGER,
    line_no INTEGER,
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(summary_id) REFERENCES statement_summary(id) ON DELETE CASCADE,
    FOREIGN KEY(business_id) REFERENCES customs_business(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_summary_item_summary ON statement_summary_item(summary_id);
CREATE INDEX IF NOT EXISTS idx_summary_item_s_ref ON statement_summary_item(s_ref);
CREATE INDEX IF NOT EXISTS idx_summary_item_n_ref ON statement_summary_item(n_ref);
CREATE INDEX IF NOT EXISTS idx_summary_item_business ON statement_summary_item(business_id);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    real_name TEXT,
    phone TEXT,
    email TEXT,
    status INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT NOT NULL UNIQUE,
    role_code TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS user_role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_role_user_id ON user_role(user_id);
CREATE INDEX IF NOT EXISTS idx_user_role_role_id ON user_role(role_id);

CREATE TABLE IF NOT EXISTS customs_process_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER,
    bl_no TEXT NOT NULL UNIQUE,
    goods_desc TEXT,
    declaration_date TEXT,
    port_name TEXT,
    overall_status TEXT NOT NULL DEFAULT 'PROCESSING',
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(business_id) REFERENCES customs_business(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_process_record_status ON customs_process_record(overall_status);
CREATE INDEX IF NOT EXISTS idx_process_record_date ON customs_process_record(declaration_date);

CREATE TABLE IF NOT EXISTS customs_process_step (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL,
    step_no INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    completion_time TEXT,
    step_desc TEXT,
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(process_id, step_no),
    FOREIGN KEY(process_id) REFERENCES customs_process_record(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_process_step_process_id ON customs_process_step(process_id);
CREATE INDEX IF NOT EXISTS idx_process_step_status ON customs_process_step(status);

CREATE TABLE IF NOT EXISTS customs_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    related_process_id INTEGER,
    occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(related_process_id) REFERENCES customs_process_record(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_activity_occurred_at ON customs_activity(occurred_at);

CREATE TABLE IF NOT EXISTS fx_rate_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_currency TEXT NOT NULL,
    quote_currency TEXT NOT NULL,
    rate TEXT NOT NULL,
    source TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(base_currency, quote_currency)
);

CREATE TABLE IF NOT EXISTS customs_cost_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_record_id INTEGER,
    record_no TEXT NOT NULL UNIQUE,
    customs_fee TEXT NOT NULL DEFAULT '0',
    refund_fee TEXT NOT NULL DEFAULT '0',
    usd_amount TEXT NOT NULL DEFAULT '0',
    usd_rate TEXT NOT NULL DEFAULT '1',
    other_fees TEXT NOT NULL DEFAULT '0',
    total_qty TEXT NOT NULL DEFAULT '0',
    total_base TEXT NOT NULL DEFAULT '0',
    per_unit_cost TEXT NOT NULL DEFAULT '0',
    currency TEXT NOT NULL DEFAULT 'BRL',
    note TEXT,
    created_by INTEGER,
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(process_record_id) REFERENCES customs_process_record(id) ON DELETE SET NULL,
    FOREIGN KEY(created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_cost_record_process_id ON customs_cost_record(process_record_id);
CREATE INDEX IF NOT EXISTS idx_cost_record_created_time ON customs_cost_record(created_time);

CREATE TABLE IF NOT EXISTS customs_cost_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cost_record_id INTEGER NOT NULL,
    line_no INTEGER,
    product_name TEXT,
    qty TEXT NOT NULL DEFAULT '0',
    allocation_cost TEXT NOT NULL DEFAULT '0',
    unit_cost TEXT NOT NULL DEFAULT '0',
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(cost_record_id) REFERENCES customs_cost_record(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cost_item_cost_record_id ON customs_cost_item(cost_record_id);

CREATE TABLE IF NOT EXISTS ai_audit_run (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    cost_record_id INTEGER,
    source TEXT NOT NULL DEFAULT 'RULE',
    model_name TEXT,
    status TEXT NOT NULL DEFAULT 'PROCESSING',
    risk_level TEXT,
    score REAL,
    summary TEXT,
    checks_json TEXT,
    input_json TEXT,
    raw_output TEXT,
    error_message TEXT,
    created_by INTEGER,
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(business_id) REFERENCES customs_business(id) ON DELETE CASCADE,
    FOREIGN KEY(cost_record_id) REFERENCES customs_cost_record(id) ON DELETE SET NULL,
    FOREIGN KEY(created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_ai_audit_run_business_id ON ai_audit_run(business_id);
CREATE INDEX IF NOT EXISTS idx_ai_audit_run_status ON ai_audit_run(status);
CREATE INDEX IF NOT EXISTS idx_ai_audit_run_created_time ON ai_audit_run(created_time);

CREATE TABLE IF NOT EXISTS ai_audit_finding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_run_id INTEGER NOT NULL,
    finding_type TEXT NOT NULL DEFAULT 'RISK',
    severity TEXT NOT NULL DEFAULT 'MEDIUM',
    rule_code TEXT,
    title TEXT NOT NULL,
    description TEXT,
    evidence TEXT,
    suggestion TEXT,
    amount TEXT,
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(audit_run_id) REFERENCES ai_audit_run(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ai_audit_finding_run_id ON ai_audit_finding(audit_run_id);
CREATE INDEX IF NOT EXISTS idx_ai_audit_finding_severity ON ai_audit_finding(severity);

CREATE TABLE IF NOT EXISTS ai_finance_review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cost_record_id INTEGER NOT NULL,
    source TEXT NOT NULL DEFAULT 'RULE',
    model_name TEXT,
    status TEXT NOT NULL DEFAULT 'PROCESSING',
    health_level TEXT,
    score REAL,
    summary TEXT,
    metrics_json TEXT,
    input_json TEXT,
    raw_output TEXT,
    error_message TEXT,
    created_by INTEGER,
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(cost_record_id) REFERENCES customs_cost_record(id) ON DELETE CASCADE,
    FOREIGN KEY(created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_ai_finance_review_cost_record_id ON ai_finance_review(cost_record_id);
CREATE INDEX IF NOT EXISTS idx_ai_finance_review_status ON ai_finance_review(status);
CREATE INDEX IF NOT EXISTS idx_ai_finance_review_created_time ON ai_finance_review(created_time);

CREATE TABLE IF NOT EXISTS ai_finance_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finance_review_id INTEGER NOT NULL,
    severity TEXT NOT NULL DEFAULT 'MEDIUM',
    title TEXT NOT NULL,
    description TEXT,
    recommendation TEXT,
    created_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(finance_review_id) REFERENCES ai_finance_review(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ai_finance_item_review_id ON ai_finance_item(finance_review_id);
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
            self.initialize_auth_seed(conn)
            self.initialize_process_seed(conn)
            self.initialize_cost_seed(conn)
            self.initialize_summary_seed(conn)

    def initialize_auth_seed(self, conn) -> None:
        role_rows = [
            ("超级管理员", "SUPER_ADMIN", "系统最高权限"),
            ("管理员", "ADMIN", "管理系统数据"),
            ("货代", "FORWARDER", "货代业务角色"),
            ("报关员", "CUSTOMS", "报关业务角色"),
            ("财务人员", "FINANCE", "财务业务角色"),
        ]
        conn.executemany(
            "INSERT OR IGNORE INTO roles (role_name, role_code, description) VALUES (?, ?, ?)",
            role_rows,
        )

        admin_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123456")
        admin_hash = hashlib.sha256(admin_password.encode("utf-8")).hexdigest()
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password, real_name, status, email) VALUES (?, ?, ?, 1, ?)",
            (admin_username, admin_hash, "系统管理员", "admin@portabrasil.local"),
        )
        admin_row = conn.execute("SELECT id FROM users WHERE username = ?", (admin_username,)).fetchone()
        role_row = conn.execute("SELECT id FROM roles WHERE role_code = 'SUPER_ADMIN'").fetchone()
        if admin_row and role_row:
            conn.execute(
                "INSERT OR IGNORE INTO user_role (user_id, role_id) VALUES (?, ?)",
                (int(admin_row[0]), int(role_row[0])),
            )

    def initialize_process_seed(self, conn) -> None:
        rows = conn.execute("SELECT COUNT(*) FROM customs_process_record").fetchone()
        if rows and int(rows[0]) > 0:
            return

        process_rows = [
            ("BR2023082401", "工业机械零件", "2023-08-24", "Santos (SSZ)", "PROCESSING"),
            ("BR2023082109", "电子消费产品", "2023-08-21", "Paranaguá (PNG)", "CLEARED"),
            ("BR2023081944", "纺织原材料", "2023-08-19", "Rio de Janeiro", "INSPECTION"),
            ("BR2023081522", "医疗器械设备", "2023-08-15", "Santos (SSZ)", "CLEARED"),
            ("BR2023081011", "汽车零配件", "2023-08-10", "Itajaí (ITJ)", "CLEARED"),
        ]
        conn.executemany(
            "INSERT INTO customs_process_record (bl_no, goods_desc, declaration_date, port_name, overall_status) VALUES (?, ?, ?, ?, ?)",
            process_rows,
        )

        process_items = conn.execute("SELECT id, bl_no, overall_status FROM customs_process_record").fetchall()
        step_rows: list[tuple[int, int, str, str | None, str]] = []
        for item in process_items:
            process_id = int(item[0])
            bl_no = str(item[1])
            overall_status = str(item[2])
            for step_no in range(1, 11):
                status = "PENDING"
                completion_time: str | None = None
                if overall_status == "CLEARED":
                    status = "COMPLETE"
                    completion_time = f"08-{step_no + 10:02d} 08:10"
                elif overall_status == "INSPECTION":
                    status = "COMPLETE" if step_no <= 6 else "PENDING"
                    completion_time = f"08-{step_no + 10:02d} 08:10" if step_no <= 6 else None
                else:
                    status = "COMPLETE" if step_no <= 3 else "PENDING"
                    completion_time = f"08-{step_no + 20:02d} 08:10" if step_no <= 3 else None
                step_rows.append((process_id, step_no, status, completion_time, f"{bl_no} - step {step_no}"))

        conn.executemany(
            "INSERT INTO customs_process_step (process_id, step_no, status, completion_time, step_desc) VALUES (?, ?, ?, ?, ?)",
            step_rows,
        )

        activity_rows = [
            ("ALERT", "海关查验通知", "集装箱号 TCNU8473629 被抽中例行查验。"),
            ("SUCCESS", "税费计算完成", "提单号 BR2023082401 关税已计算完成，等待支付。"),
            ("INFO", "文件审核通过", "商业发票和装箱单已通过巴西海关审核系统 (Siscomex)。"),
        ]
        conn.executemany(
            "INSERT INTO customs_activity (activity_type, title, description) VALUES (?, ?, ?)",
            activity_rows,
        )

    def initialize_cost_seed(self, conn) -> None:
        rows = conn.execute("SELECT COUNT(*) FROM customs_cost_record").fetchone()
        if rows and int(rows[0]) > 0:
            return

        process_row = conn.execute("SELECT id FROM customs_process_record ORDER BY id ASC LIMIT 1").fetchone()
        admin_row = conn.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
        if not process_row:
            return

        record_no = f"COST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        record_id = conn.execute(
            "INSERT INTO customs_cost_record (process_record_id, record_no, customs_fee, refund_fee, usd_amount, usd_rate, other_fees, total_qty, total_base, per_unit_cost, note, created_by) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                int(process_row[0]),
                record_no,
                "125000.00",
                "2000.00",
                "3000.00",
                "5.1200",
                "1800.00",
                "600.00",
                "140160.00",
                "233.6000",
                "初始化示例成本记录",
                int(admin_row[0]) if admin_row else None,
            ),
        ).lastrowid

        item_rows = [
            (record_id, 1, "工业机械零件A", "250", "58400.00", "233.6000"),
            (record_id, 2, "工业机械零件B", "350", "81760.00", "233.6000"),
        ]
        conn.executemany(
            "INSERT INTO customs_cost_item (cost_record_id, line_no, product_name, qty, allocation_cost, unit_cost) VALUES (?, ?, ?, ?, ?, ?)",
            item_rows,
        )

        conn.execute(
            "INSERT OR REPLACE INTO fx_rate_cache (base_currency, quote_currency, rate, source, updated_at) VALUES (?, ?, ?, ?, ?)",
            ("USD", "BRL", "5.1200", "seed", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )

    def initialize_summary_seed(self, conn) -> None:
        rows = conn.execute("SELECT COUNT(*) FROM statement_summary").fetchone()
        if rows and int(rows[0]) > 0:
            return

        summary_id = conn.execute(
            "INSERT INTO statement_summary (statement_no, issue_date, due_date, total_amount, amount_direction, customer_name, issuer_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("050/25", "2025-08-01", "2025-08-31", "58400.00", "S/Favor", "进口商客户A", "PortaBrasil Logistica"),
        ).lastrowid

        item_rows = [
            (summary_id, None, "S/REF-001", "NF-12345", "S/Favor", "12500.00", None, 1),
            (summary_id, None, "S/REF-002", "NF-12346", "S/Favor", "23000.00", None, 2),
            (summary_id, None, "S/REF-003", "NF-12347", "S/Favor", "22900.00", None, 3),
        ]
        conn.executemany(
            "INSERT INTO statement_summary_item (summary_id, n_ref, s_ref, nf_no, amount_direction, balance_amount, business_id, line_no) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            item_rows,
        )

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
