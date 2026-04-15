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


SET FOREIGN_KEY_CHECKS = 1;