-- Add direct business linkage to cost records for existing MySQL databases.
-- Run once after backing up the database.

ALTER TABLE customs_cost_record
    ADD COLUMN business_id BIGINT UNSIGNED NULL COMMENT '可选关联 customs_business.id' AFTER id,
    ADD KEY idx_business_id (business_id),
    ADD CONSTRAINT fk_cost_record_business
        FOREIGN KEY (business_id) REFERENCES customs_business(id)
        ON DELETE SET NULL ON UPDATE CASCADE;

UPDATE customs_cost_record cr
JOIN customs_process_record p ON p.id = cr.process_record_id
SET cr.business_id = p.business_id
WHERE cr.business_id IS NULL
  AND p.business_id IS NOT NULL;
