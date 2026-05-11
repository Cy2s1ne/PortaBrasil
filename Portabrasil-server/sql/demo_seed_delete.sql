-- PortaBrasil demo data cleanup script.
--
-- Usage:
--   SQLite:
--     cd Portabrasil-server
--     sqlite3 instance/portabrasil.db < sql/demo_seed_delete.sql
--
--   MySQL:
--     mysql -u root -p portabrasil < sql/demo_seed_delete.sql
--
-- This script removes only the demo data inserted by sql/demo_seed.sql.

BEGIN;

-- AI finance review data ----------------------------------------------------
DELETE FROM ai_finance_item
WHERE finance_review_id IN (
    SELECT fr.id
    FROM ai_finance_review fr
    JOIN customs_cost_record c ON c.id = fr.cost_record_id
    WHERE c.record_no IN (
        'COST-DEMO-20260428-001',
        'COST-DEMO-20260508-002',
        'COST-DEMO-20260509-004'
    )
);

DELETE FROM ai_finance_review
WHERE cost_record_id IN (
    SELECT id
    FROM customs_cost_record
    WHERE record_no IN (
        'COST-DEMO-20260428-001',
        'COST-DEMO-20260508-002',
        'COST-DEMO-20260509-004'
    )
);

-- AI audit data -------------------------------------------------------------
DELETE FROM ai_audit_finding
WHERE audit_run_id IN (
    SELECT r.id
    FROM ai_audit_run r
    JOIN customs_business b ON b.id = r.business_id
    WHERE b.s_ref IN (
        'S/2026-IMP-001',
        'S/2026-IMP-002',
        'S/2026-EXP-003',
        'S/2026-IMP-004',
        'S/2026-IMP-005'
    )
);

DELETE FROM ai_audit_run
WHERE business_id IN (
    SELECT id
    FROM customs_business
    WHERE s_ref IN (
        'S/2026-IMP-001',
        'S/2026-IMP-002',
        'S/2026-EXP-003',
        'S/2026-IMP-004',
        'S/2026-IMP-005'
    )
);

-- Statement summary data ----------------------------------------------------
DELETE FROM statement_summary_item
WHERE summary_id IN (
    SELECT id
    FROM statement_summary
    WHERE statement_no = 'DEMO-0526-AUDIT'
);

DELETE FROM statement_summary
WHERE statement_no = 'DEMO-0526-AUDIT';

-- Cost data -----------------------------------------------------------------
DELETE FROM customs_cost_item
WHERE cost_record_id IN (
    SELECT id
    FROM customs_cost_record
    WHERE record_no IN (
        'COST-DEMO-20260428-001',
        'COST-DEMO-20260508-002',
        'COST-DEMO-20260509-004'
    )
);

DELETE FROM customs_cost_record
WHERE record_no IN (
    'COST-DEMO-20260428-001',
    'COST-DEMO-20260508-002',
    'COST-DEMO-20260509-004'
);

-- Process data --------------------------------------------------------------
DELETE FROM customs_activity
WHERE title IN (
    '审计完成：S/2026-IMP-001',
    '审计预警：S/2026-IMP-002',
    '流程推进：S/2026-IMP-004'
);

DELETE FROM customs_process_step
WHERE process_id IN (
    SELECT id
    FROM customs_process_record
    WHERE bl_no IN (
        'BL-DEMO-SSZ-001',
        'BL-DEMO-ITJ-002',
        'BL-DEMO-PNG-003',
        'BL-DEMO-GIG-004',
        'BL-DEMO-VCP-005'
    )
);

DELETE FROM customs_process_record
WHERE bl_no IN (
    'BL-DEMO-SSZ-001',
    'BL-DEMO-ITJ-002',
    'BL-DEMO-PNG-003',
    'BL-DEMO-GIG-004',
    'BL-DEMO-VCP-005'
);

-- Business data -------------------------------------------------------------
DELETE FROM customs_business_fee_item
WHERE business_id IN (
    SELECT id
    FROM customs_business
    WHERE s_ref IN (
        'S/2026-IMP-001',
        'S/2026-IMP-002',
        'S/2026-EXP-003',
        'S/2026-IMP-004',
        'S/2026-IMP-005'
    )
);

DELETE FROM customs_business
WHERE s_ref IN (
    'S/2026-IMP-001',
    'S/2026-IMP-002',
    'S/2026-EXP-003',
    'S/2026-IMP-004',
    'S/2026-IMP-005'
);

-- Source PDF and parse task data -------------------------------------------
DELETE FROM pdf_parse_task
WHERE task_no IN (
    'TASK-DEMO-20260421-001',
    'TASK-DEMO-20260425-002',
    'TASK-DEMO-20260428-003'
);

DELETE FROM pdf_file
WHERE file_hash IN (
    'demo_hash_santos_001',
    'demo_hash_itajai_002',
    'demo_hash_paranagua_003'
);

-- Demo user data ------------------------------------------------------------
DELETE FROM user_role
WHERE user_id IN (
    SELECT id
    FROM users
    WHERE username = 'demo_auditor'
);

DELETE FROM users
WHERE username = 'demo_auditor';

COMMIT;
