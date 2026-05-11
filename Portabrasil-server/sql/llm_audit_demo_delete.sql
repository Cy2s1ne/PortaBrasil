-- Delete LLM audit demo input data and any generated audit results.

BEGIN;

DELETE FROM ai_audit_finding
WHERE audit_run_id IN (
    SELECT id
    FROM ai_audit_run
    WHERE business_id IN (11101, 11102, 11103)
);

DELETE FROM ai_audit_run
WHERE business_id IN (11101, 11102, 11103);

DELETE FROM ai_finance_item
WHERE finance_review_id IN (
    SELECT id
    FROM ai_finance_review
    WHERE cost_record_id IN (11601, 11602, 11603)
);

DELETE FROM ai_finance_review
WHERE cost_record_id IN (11601, 11602, 11603);

DELETE FROM customs_cost_item WHERE cost_record_id IN (11601, 11602, 11603);
DELETE FROM customs_cost_record WHERE id IN (11601, 11602, 11603);

DELETE FROM customs_business_fee_item WHERE business_id IN (11101, 11102, 11103);
DELETE FROM customs_business WHERE id IN (11101, 11102, 11103);

COMMIT;
