-- 适用于已有 MySQL 数据库的增量迁移（不会删除已有业务数据）
-- 执行示例：
-- mysql -u root -p portabrasil < Portabrasil-server/sql/migrations/20260416_add_cost_module_tables.sql

CREATE TABLE IF NOT EXISTS fx_rate_cache (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    base_currency VARCHAR(10) NOT NULL,
    quote_currency VARCHAR(10) NOT NULL,
    rate DECIMAL(18,6) NOT NULL,
    source VARCHAR(50) DEFAULT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_fx_pair (base_currency, quote_currency),
    KEY idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='汇率缓存表';

CREATE TABLE IF NOT EXISTS customs_cost_record (
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

CREATE TABLE IF NOT EXISTS customs_cost_item (
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
VALUES ('USD', 'BRL', 5.120000, 'seed', NOW())
ON DUPLICATE KEY UPDATE rate = VALUES(rate), source = VALUES(source), updated_at = VALUES(updated_at);
