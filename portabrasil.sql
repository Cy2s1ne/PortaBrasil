-- =========================================================
-- 海关 PDF 单据解析系统 - 最小可用版本
-- Database: MySQL 8.x
-- Charset : utf8mb4
-- =========================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- =========================================================
-- 1. 原始 PDF 文件表
-- =========================================================
DROP TABLE IF EXISTS pdf_file;
CREATE TABLE pdf_file (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    file_size BIGINT UNSIGNED DEFAULT NULL COMMENT '文件大小(字节)',
    file_hash VARCHAR(64) DEFAULT NULL COMMENT '文件哈希值，便于去重',
    page_count INT DEFAULT NULL COMMENT 'PDF页数',
    parse_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '解析状态: PENDING/PROCESSING/SUCCESS/FAILED',
    upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
    PRIMARY KEY (id),
    UNIQUE KEY uk_file_hash (file_hash),
    KEY idx_parse_status (parse_status),
    KEY idx_upload_time (upload_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='原始PDF文件表';


-- =========================================================
-- 2. PDF 解析任务表
-- =========================================================
DROP TABLE IF EXISTS pdf_parse_task;
CREATE TABLE pdf_parse_task (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    file_id BIGINT UNSIGNED NOT NULL COMMENT '关联pdf_file.id',
    task_no VARCHAR(64) NOT NULL COMMENT '任务编号',
    parser_type VARCHAR(50) NOT NULL DEFAULT 'LLM' COMMENT '解析方式: LLM/OCR/RULE',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '任务状态: PENDING/PROCESSING/SUCCESS/FAILED',
    start_time DATETIME DEFAULT NULL COMMENT '开始时间',
    end_time DATETIME DEFAULT NULL COMMENT '结束时间',
    error_message TEXT DEFAULT NULL COMMENT '错误信息',
    raw_result LONGTEXT DEFAULT NULL COMMENT 'LLM原始解析结果(JSON文本)',
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_task_no (task_no),
    KEY idx_file_id (file_id),
    KEY idx_status (status),
    CONSTRAINT fk_parse_task_file
        FOREIGN KEY (file_id) REFERENCES pdf_file(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='PDF解析任务表';


-- =========================================================
-- 3. 海关业务主表（核心表，一条记录对应一个 S/Ref）
-- =========================================================
DROP TABLE IF EXISTS customs_business;
CREATE TABLE customs_business (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    s_ref VARCHAR(50) NOT NULL COMMENT '核心业务编号 S/Ref',
    n_ref VARCHAR(50) DEFAULT NULL COMMENT 'N/Referencia 或 No. Processo',
    document_no VARCHAR(50) DEFAULT NULL COMMENT '单据号，如 Demonstrativo No.',
    invoice_no VARCHAR(100) DEFAULT NULL COMMENT 'No. Invoice',
    nf_no VARCHAR(100) DEFAULT NULL COMMENT 'No. NF / No. NFS-e',
    process_no VARCHAR(50) DEFAULT NULL COMMENT '流程号/业务号',
    business_type VARCHAR(20) DEFAULT NULL COMMENT '业务类型: IMPORT/EXPORT',
    trade_company VARCHAR(255) DEFAULT NULL COMMENT 'Export/Import 对应公司',
    customer_name VARCHAR(255) DEFAULT NULL COMMENT '客户名称',
    customer_address VARCHAR(500) DEFAULT NULL COMMENT '客户地址',
    customer_city VARCHAR(100) DEFAULT NULL COMMENT '客户城市',
    customer_state VARCHAR(50) DEFAULT NULL COMMENT '客户州/省',
    customer_zip_code VARCHAR(30) DEFAULT NULL COMMENT '客户邮编',
    customer_tax_no VARCHAR(100) DEFAULT NULL COMMENT '客户税号 CNPJ/CPF',
    issuer_name VARCHAR(255) DEFAULT NULL COMMENT '开单公司名称',
    issuer_tax_no VARCHAR(100) DEFAULT NULL COMMENT '开单公司税号',
    mawb_mbl VARCHAR(100) DEFAULT NULL COMMENT 'MAWB / MBL',
    hawb_hbl VARCHAR(100) DEFAULT NULL COMMENT 'HAWB / HBL',
    di_duimp_due VARCHAR(100) DEFAULT NULL COMMENT 'DI/DUIMP/DUE',
    registration_date DATE DEFAULT NULL COMMENT 'Reg 日期',
    arrival_date DATE DEFAULT NULL COMMENT 'Chegada 到港日期',
    customs_clearance_date DATE DEFAULT NULL COMMENT 'Desembaraço 清关日期',
    loading_date DATE DEFAULT NULL COMMENT 'Carregamento 装载日期',
    destination VARCHAR(100) DEFAULT NULL COMMENT '目的地',
    vessel_flight_name VARCHAR(100) DEFAULT NULL COMMENT '船名/航班名',
    gross_weight DECIMAL(18,3) DEFAULT NULL COMMENT '毛重',
    volume_count INT DEFAULT NULL COMMENT '件数',
    cargo_desc VARCHAR(255) DEFAULT NULL COMMENT '货物描述',
    freight_currency VARCHAR(10) DEFAULT NULL COMMENT '运费币种',
    freight_amount DECIMAL(18,2) DEFAULT NULL COMMENT '运费金额',
    fob_currency VARCHAR(10) DEFAULT NULL COMMENT 'FOB币种',
    fob_amount DECIMAL(18,2) DEFAULT NULL COMMENT 'FOB金额',
    cif_currency VARCHAR(10) DEFAULT NULL COMMENT 'CIF币种',
    cif_amount DECIMAL(18,2) DEFAULT NULL COMMENT 'CIF金额',
    cif_brl_amount DECIMAL(18,2) DEFAULT NULL COMMENT '本币口径的CIF/FOB金额',
    dollar_rate DECIMAL(18,6) DEFAULT NULL COMMENT '美元汇率',
    euro_rate DECIMAL(18,6) DEFAULT NULL COMMENT '欧元汇率',
    total_credit DECIMAL(18,2) DEFAULT NULL COMMENT '总贷方',
    total_debit DECIMAL(18,2) DEFAULT NULL COMMENT '总借方',
    balance_amount DECIMAL(18,2) DEFAULT NULL COMMENT '余额',
    balance_direction VARCHAR(20) DEFAULT NULL COMMENT '余额方向: FAVOR/PAYABLE',
    source_file_id BIGINT UNSIGNED DEFAULT NULL COMMENT '来源PDF文件ID',
    source_page_no INT DEFAULT NULL COMMENT '来源页码',
    data_status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' COMMENT '数据状态: DRAFT/CONFIRMED/REVIEWING',
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_s_ref (s_ref),
    KEY idx_n_ref (n_ref),
    KEY idx_invoice_no (invoice_no),
    KEY idx_nf_no (nf_no),
    KEY idx_customer_name (customer_name),
    KEY idx_source_file_id (source_file_id),
    CONSTRAINT fk_business_file
        FOREIGN KEY (source_file_id) REFERENCES pdf_file(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='海关业务主表（以S/Ref为核心）';


-- =========================================================
-- 4. 海关业务费用明细表
-- =========================================================
DROP TABLE IF EXISTS customs_business_fee_item;
CREATE TABLE customs_business_fee_item (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    business_id BIGINT UNSIGNED NOT NULL COMMENT '关联 customs_business.id',
    fee_date DATE DEFAULT NULL COMMENT '费用日期',
    fee_code VARCHAR(20) DEFAULT NULL COMMENT '费用代码',
    fee_name VARCHAR(255) NOT NULL COMMENT '费用名称',
    credit_amount DECIMAL(18,2) DEFAULT NULL COMMENT '贷方金额',
    debit_amount DECIMAL(18,2) DEFAULT NULL COMMENT '借方金额',
    line_no INT DEFAULT NULL COMMENT '原始行号',
    raw_text VARCHAR(500) DEFAULT NULL COMMENT '原始文本',
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_business_id (business_id),
    KEY idx_fee_code (fee_code),
    KEY idx_fee_date (fee_date),
    CONSTRAINT fk_fee_item_business
        FOREIGN KEY (business_id) REFERENCES customs_business(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='海关业务费用明细表';


-- =========================================================
-- 5. 汇总单主表（例如 Fatura）
-- =========================================================
DROP TABLE IF EXISTS statement_summary;
CREATE TABLE statement_summary (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    statement_no VARCHAR(50) NOT NULL COMMENT '汇总单号，如 050/25',
    issue_date DATE DEFAULT NULL COMMENT '开具日期',
    due_date DATE DEFAULT NULL COMMENT '到期日期',
    total_amount DECIMAL(18,2) DEFAULT NULL COMMENT '总金额',
    amount_direction VARCHAR(20) DEFAULT NULL COMMENT '金额方向，如 S/Favor',
    customer_name VARCHAR(255) DEFAULT NULL COMMENT '客户名称',
    customer_address VARCHAR(500) DEFAULT NULL COMMENT '客户地址',
    customer_city VARCHAR(100) DEFAULT NULL COMMENT '客户城市',
    customer_state VARCHAR(50) DEFAULT NULL COMMENT '客户州/省',
    customer_zip_code VARCHAR(30) DEFAULT NULL COMMENT '客户邮编',
    customer_tax_no VARCHAR(100) DEFAULT NULL COMMENT '客户税号',
    issuer_name VARCHAR(255) DEFAULT NULL COMMENT '开单公司名称',
    source_file_id BIGINT UNSIGNED DEFAULT NULL COMMENT '来源PDF文件ID',
    source_page_no INT DEFAULT NULL COMMENT '来源页码',
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_statement_no (statement_no),
    KEY idx_source_file_id (source_file_id),
    CONSTRAINT fk_summary_file
        FOREIGN KEY (source_file_id) REFERENCES pdf_file(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='汇总单主表';


-- =========================================================
-- 6. 汇总单明细表
-- =========================================================
DROP TABLE IF EXISTS statement_summary_item;
CREATE TABLE statement_summary_item (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    summary_id BIGINT UNSIGNED NOT NULL COMMENT '关联 statement_summary.id',
    n_ref VARCHAR(50) DEFAULT NULL COMMENT 'N/Referencia',
    s_ref VARCHAR(50) DEFAULT NULL COMMENT 'S/Referencia',
    nf_no VARCHAR(100) DEFAULT NULL COMMENT 'No. NF',
    amount_direction VARCHAR(20) DEFAULT NULL COMMENT '金额方向，如 S/Favor',
    balance_amount DECIMAL(18,2) DEFAULT NULL COMMENT 'Saldo/余额',
    business_id BIGINT UNSIGNED DEFAULT NULL COMMENT '可选，关联 customs_business.id',
    line_no INT DEFAULT NULL COMMENT '原始行号',
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_summary_id (summary_id),
    KEY idx_s_ref (s_ref),
    KEY idx_n_ref (n_ref),
    KEY idx_business_id (business_id),
    CONSTRAINT fk_summary_item_summary
        FOREIGN KEY (summary_id) REFERENCES statement_summary(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_summary_item_business
        FOREIGN KEY (business_id) REFERENCES customs_business(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='汇总单明细表';

-- =========================================================
-- 6.5 AI 审计/财务分析表（预清理，避免后续外键冲突）
-- =========================================================
DROP TABLE IF EXISTS ai_finance_item;
DROP TABLE IF EXISTS ai_finance_review;
DROP TABLE IF EXISTS ai_audit_finding;
DROP TABLE IF EXISTS ai_audit_run;


SET FOREIGN_KEY_CHECKS = 1;

-- =========================================================
-- 7. 用户表
-- =========================================================
DROP TABLE IF EXISTS user_role;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    real_name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),

    status TINYINT DEFAULT 1, -- 1正常 0禁用

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================================
-- 8. 角色表
-- =========================================================
CREATE TABLE roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    role_code VARCHAR(50) NOT NULL UNIQUE, -- 用于程序判断
    description VARCHAR(255)
);

-- =========================================================
-- 9. 用户-角色关联表
-- =========================================================
CREATE TABLE user_role (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_role (user_id, role_id),
    KEY idx_user_id (user_id),
    KEY idx_role_id (role_id),
    CONSTRAINT fk_user_role_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_user_role_role
        FOREIGN KEY (role_id) REFERENCES roles(id)
        ON DELETE CASCADE ON UPDATE CASCADE
);


INSERT INTO roles (role_name, role_code, description) VALUES
('超级管理员', 'SUPER_ADMIN', '系统最高权限'),
('管理员', 'ADMIN', '管理系统数据'),
('货代', 'FORWARDER', '货代业务角色'),
('报关员', 'CUSTOMS', '报关业务角色'),
('财务人员', 'FINANCE', '财务业务角色');

-- 默认管理员：admin / admin123456（SHA-256）
INSERT INTO users (username, password, real_name, status, email)
VALUES ('admin', 'ac0e7d037817094e9e0b4441f9bae3209d67b02fa484917065f71b16109a1a78', '系统管理员', 1, 'admin@portabrasil.local');

INSERT INTO user_role (user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN roles r ON r.role_code = 'SUPER_ADMIN'
WHERE u.username = 'admin';

-- =========================================================
-- 10. 清关流程主记录表
-- =========================================================
DROP TABLE IF EXISTS customs_process_step;
DROP TABLE IF EXISTS customs_activity;
DROP TABLE IF EXISTS customs_process_record;

CREATE TABLE customs_process_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    business_id BIGINT UNSIGNED NULL COMMENT '可选关联 customs_business.id', -- 修改点：增加 UNSIGNED
    bl_no VARCHAR(64) NOT NULL UNIQUE COMMENT '提单号',
    goods_desc VARCHAR(255) NULL COMMENT '货物描述',
    declaration_date DATE NULL COMMENT '申报日期',
    port_name VARCHAR(100) NULL COMMENT '港口',
    overall_status VARCHAR(20) NOT NULL DEFAULT 'PROCESSING' COMMENT 'PROCESSING/CLEARED/INSPECTION',
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_overall_status (overall_status),
    KEY idx_declaration_date (declaration_date),
    CONSTRAINT fk_process_business
        FOREIGN KEY (business_id) REFERENCES customs_business(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='清关流程主记录表';

-- =========================================================
-- 11. 清关流程步骤表（10步）
-- =========================================================
CREATE TABLE customs_process_step (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    process_id BIGINT NOT NULL COMMENT '关联 customs_process_record.id',
    step_no TINYINT NOT NULL COMMENT '步骤号 1-10',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/COMPLETE',
    completion_time VARCHAR(20) NULL COMMENT '完成时间（前端格式）',
    step_desc VARCHAR(255) NULL COMMENT '步骤描述',
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_process_step (process_id, step_no),
    KEY idx_process_id (process_id),
    KEY idx_step_status (status),
    CONSTRAINT fk_process_step_record
        FOREIGN KEY (process_id) REFERENCES customs_process_record(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='清关流程步骤表';

-- =========================================================
-- 12. 首页动态表
-- =========================================================
CREATE TABLE customs_activity (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    activity_type VARCHAR(20) NOT NULL COMMENT 'ALERT/SUCCESS/INFO',
    title VARCHAR(120) NOT NULL COMMENT '动态标题',
    description VARCHAR(255) NOT NULL COMMENT '动态描述',
    related_process_id BIGINT NULL COMMENT '可选关联流程记录',
    occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发生时间',
    KEY idx_occurred_at (occurred_at),
    CONSTRAINT fk_activity_process
        FOREIGN KEY (related_process_id) REFERENCES customs_process_record(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='首页动态表';

INSERT INTO customs_process_record (bl_no, goods_desc, declaration_date, port_name, overall_status) VALUES
('BR2023082401', '工业机械零件', '2023-08-24', 'Santos (SSZ)', 'PROCESSING'),
('BR2023082109', '电子消费产品', '2023-08-21', 'Paranaguá (PNG)', 'CLEARED'),
('BR2023081944', '纺织原材料', '2023-08-19', 'Rio de Janeiro', 'INSPECTION'),
('BR2023081522', '医疗器械设备', '2023-08-15', 'Santos (SSZ)', 'CLEARED'),
('BR2023081011', '汽车零配件', '2023-08-10', 'Itajaí (ITJ)', 'CLEARED');

INSERT INTO customs_process_step (process_id, step_no, status, completion_time, step_desc)
SELECT p.id, s.step_no,
    CASE
        WHEN p.overall_status = 'CLEARED' THEN 'COMPLETE'
        WHEN p.overall_status = 'INSPECTION' AND s.step_no <= 6 THEN 'COMPLETE'
        WHEN p.overall_status = 'PROCESSING' AND s.step_no <= 3 THEN 'COMPLETE'
        ELSE 'PENDING'
    END AS step_status,
    CASE
        WHEN p.overall_status = 'CLEARED' THEN CONCAT('08-', LPAD(s.step_no + 10, 2, '0'), ' 08:10')
        WHEN p.overall_status = 'INSPECTION' AND s.step_no <= 6 THEN CONCAT('08-', LPAD(s.step_no + 10, 2, '0'), ' 08:10')
        WHEN p.overall_status = 'PROCESSING' AND s.step_no <= 3 THEN CONCAT('08-', LPAD(s.step_no + 20, 2, '0'), ' 08:10')
        ELSE NULL
    END AS completion_time,
    CONCAT(p.bl_no, ' - step ', s.step_no) AS step_desc
FROM customs_process_record p
JOIN (
    SELECT 1 AS step_no UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
    UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10
) s;

INSERT INTO customs_activity (activity_type, title, description) VALUES
('ALERT', '海关查验通知', '集装箱号 TCNU8473629 被抽中例行查验。'),
('SUCCESS', '税费计算完成', '提单号 BR2023082401 关税已计算完成，等待支付。'),
('INFO', '文件审核通过', '商业发票和装箱单已通过巴西海关审核系统 (Siscomex)。');

-- =========================================================
-- 13. 汇率缓存表
-- =========================================================
DROP TABLE IF EXISTS fx_rate_cache;
CREATE TABLE fx_rate_cache (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    base_currency VARCHAR(10) NOT NULL,
    quote_currency VARCHAR(10) NOT NULL,
    rate DECIMAL(18,6) NOT NULL,
    source VARCHAR(50) DEFAULT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_fx_pair (base_currency, quote_currency),
    KEY idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='汇率缓存表';

-- =========================================================
-- 14. 成本分析主表
-- =========================================================
DROP TABLE IF EXISTS customs_cost_item;
DROP TABLE IF EXISTS customs_cost_record;

CREATE TABLE customs_cost_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    process_record_id BIGINT NULL COMMENT '可选关联 customs_process_record.id',
    record_no VARCHAR(64) NOT NULL COMMENT '成本记录编号',
    customs_fee DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '海关总费用',
    refund_fee DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '退款费用',
    usd_amount DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '美元金额',
    usd_rate DECIMAL(18,6) NOT NULL DEFAULT 1 COMMENT '美元兑 BRL 汇率',
    other_fees DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '其它附加费用',
    total_qty DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '商品总数量',
    total_base DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '总成本基数',
    per_unit_cost DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '每件商品成本',
    currency VARCHAR(10) NOT NULL DEFAULT 'BRL' COMMENT '币种',
    note VARCHAR(500) NULL COMMENT '备注',
    created_by BIGINT NULL COMMENT '创建人 users.id',
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_record_no (record_no),
    KEY idx_process_record_id (process_record_id),
    KEY idx_created_time (created_time),
    CONSTRAINT fk_cost_record_process
        FOREIGN KEY (process_record_id) REFERENCES customs_process_record(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_cost_record_user
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成本分析主表';

-- =========================================================
-- 15. 成本分析商品明细表
-- =========================================================
CREATE TABLE customs_cost_item (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    cost_record_id BIGINT NOT NULL COMMENT '关联 customs_cost_record.id',
    line_no INT NULL COMMENT '行号',
    product_name VARCHAR(255) NULL COMMENT '商品名称',
    qty DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '数量',
    allocation_cost DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '分摊成本',
    unit_cost DECIMAL(18,4) NOT NULL DEFAULT 0 COMMENT '单件成本',
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_cost_record_id (cost_record_id),
    CONSTRAINT fk_cost_item_record
        FOREIGN KEY (cost_record_id) REFERENCES customs_cost_record(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成本分析商品明细表';

INSERT INTO fx_rate_cache (base_currency, quote_currency, rate, source, updated_at)
VALUES ('USD', 'BRL', 5.120000, 'seed', NOW());

INSERT INTO customs_cost_record (
    process_record_id, record_no, customs_fee, refund_fee, usd_amount, usd_rate, other_fees,
    total_qty, total_base, per_unit_cost, currency, note, created_by
)
SELECT
    p.id,
    CONCAT('COST-', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s')),
    125000.0000,
    2000.0000,
    3000.0000,
    5.120000,
    1800.0000,
    600.0000,
    140160.0000,
    233.6000,
    'BRL',
    '初始化示例成本记录',
    u.id
FROM customs_process_record p
JOIN users u ON u.username = 'admin'
ORDER BY p.id ASC
LIMIT 1;

INSERT INTO customs_cost_item (cost_record_id, line_no, product_name, qty, allocation_cost, unit_cost)
SELECT id, 1, '工业机械零件A', 250.0000, 58400.0000, 233.6000
FROM customs_cost_record
ORDER BY id DESC
LIMIT 1;

INSERT INTO customs_cost_item (cost_record_id, line_no, product_name, qty, allocation_cost, unit_cost)
SELECT id, 2, '工业机械零件B', 350.0000, 81760.0000, 233.6000
FROM customs_cost_record
ORDER BY id DESC
LIMIT 1;

-- =========================================================
-- 16. AI 审计运行记录表
-- =========================================================
CREATE TABLE ai_audit_run (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    business_id BIGINT UNSIGNED NOT NULL,
    cost_record_id BIGINT NULL,
    source VARCHAR(20) NOT NULL DEFAULT 'RULE',
    model_name VARCHAR(100) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PROCESSING',
    risk_level VARCHAR(20) NULL,
    score DECIMAL(7,2) NULL,
    summary VARCHAR(1000) NULL,
    checks_json LONGTEXT NULL,
    input_json LONGTEXT NULL,
    raw_output LONGTEXT NULL,
    error_message LONGTEXT NULL,
    created_by BIGINT NULL,
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_business_id (business_id),
    KEY idx_status (status),
    KEY idx_created_time (created_time),
    CONSTRAINT fk_ai_audit_business
        FOREIGN KEY (business_id) REFERENCES customs_business(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ai_audit_cost_record
        FOREIGN KEY (cost_record_id) REFERENCES customs_cost_record(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_ai_audit_user
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI审计运行记录';

-- =========================================================
-- 17. AI 审计发现项表
-- =========================================================
CREATE TABLE ai_audit_finding (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    audit_run_id BIGINT NOT NULL,
    finding_type VARCHAR(30) NOT NULL DEFAULT 'RISK',
    severity VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    rule_code VARCHAR(80) NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    evidence TEXT NULL,
    suggestion TEXT NULL,
    amount DECIMAL(18,4) NULL,
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_audit_run_id (audit_run_id),
    KEY idx_severity (severity),
    CONSTRAINT fk_ai_audit_finding_run
        FOREIGN KEY (audit_run_id) REFERENCES ai_audit_run(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI审计发现项';

-- =========================================================
-- 18. AI 财务分析记录表
-- =========================================================
CREATE TABLE ai_finance_review (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    cost_record_id BIGINT NOT NULL,
    source VARCHAR(20) NOT NULL DEFAULT 'RULE',
    model_name VARCHAR(100) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PROCESSING',
    health_level VARCHAR(20) NULL,
    score DECIMAL(7,2) NULL,
    summary VARCHAR(1000) NULL,
    metrics_json LONGTEXT NULL,
    input_json LONGTEXT NULL,
    raw_output LONGTEXT NULL,
    error_message LONGTEXT NULL,
    created_by BIGINT NULL,
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_cost_record_id (cost_record_id),
    KEY idx_status (status),
    KEY idx_created_time (created_time),
    CONSTRAINT fk_ai_finance_cost_record
        FOREIGN KEY (cost_record_id) REFERENCES customs_cost_record(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ai_finance_user
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI财务分析记录';

-- =========================================================
-- 19. AI 财务分析问题项表
-- =========================================================
CREATE TABLE ai_finance_item (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    finance_review_id BIGINT NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    recommendation TEXT NULL,
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_finance_review_id (finance_review_id),
    CONSTRAINT fk_ai_finance_item_review
        FOREIGN KEY (finance_review_id) REFERENCES ai_finance_review(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI财务分析问题项';
