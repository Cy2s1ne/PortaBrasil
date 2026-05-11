-- PortaBrasil demo data delete script.
-- This file removes only the records inserted by sql/demo_seed.sql.

BEGIN;

DELETE FROM statement_summary_item WHERE id BETWEEN 10211 AND 10213;
DELETE FROM statement_summary WHERE id = 10201;

DELETE FROM ai_finance_item WHERE id BETWEEN 10101 AND 10102;
DELETE FROM ai_finance_review WHERE id BETWEEN 10001 AND 10002;

DELETE FROM ai_audit_finding WHERE id BETWEEN 9901 AND 9905;
DELETE FROM ai_audit_run WHERE id BETWEEN 9801 AND 9803;

DELETE FROM customs_cost_item WHERE id BETWEEN 9701 AND 9707;
DELETE FROM customs_cost_record WHERE id BETWEEN 9601 AND 9603;

DELETE FROM customs_activity WHERE id BETWEEN 9501 AND 9503;
DELETE FROM customs_process_step WHERE id BETWEEN 9401 AND 9450;
DELETE FROM customs_process_record WHERE id BETWEEN 9301 AND 9305;

DELETE FROM customs_business_fee_item WHERE id BETWEEN 9201 AND 9224;
DELETE FROM customs_business WHERE id BETWEEN 9101 AND 9105;

DELETE FROM pdf_parse_task WHERE id BETWEEN 9001 AND 9003;
DELETE FROM pdf_file WHERE id BETWEEN 9001 AND 9003;

COMMIT;
