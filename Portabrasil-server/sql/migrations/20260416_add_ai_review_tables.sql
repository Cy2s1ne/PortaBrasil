-- 审计校验 / 财务核算 AI 结果表（增量迁移）
-- 执行示例：
-- mysql -u root -p portabrasil < Portabrasil-server/sql/migrations/20260416_add_ai_review_tables.sql

CREATE TABLE IF NOT EXISTS ai_audit_run (
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

CREATE TABLE IF NOT EXISTS ai_audit_finding (
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

CREATE TABLE IF NOT EXISTS ai_finance_review (
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

CREATE TABLE IF NOT EXISTS ai_finance_item (
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

