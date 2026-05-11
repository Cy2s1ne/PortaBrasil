-- PortaBrasil demo insert data for local development.
--
-- SQLite usage:
--   cd Portabrasil-server
--   uv run python -c "from sql.database import get_database; get_database().initialize()"
--   sqlite3 instance/portabrasil.db < sql/demo_seed.sql
--
-- MySQL usage:
--   mysql -u root -p portabrasil < sql/demo_seed.sql
--
-- The data below is idempotent by business/order numbers. It creates a richer
-- presentation dataset for business records, process tracking, cost analysis,
-- AI audit runs, audit findings, and finance reviews.

BEGIN;

-- Demo users and roles -------------------------------------------------------
INSERT INTO roles (role_name, role_code, description)
SELECT '超级管理员', 'SUPER_ADMIN', '系统最高权限'
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE role_code = 'SUPER_ADMIN');

INSERT INTO roles (role_name, role_code, description)
SELECT '报关员', 'CUSTOMS', '报关业务角色'
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE role_code = 'CUSTOMS');

INSERT INTO roles (role_name, role_code, description)
SELECT '财务人员', 'FINANCE', '财务业务角色'
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE role_code = 'FINANCE');

INSERT INTO users (username, password, real_name, phone, email, status, created_at, updated_at)
SELECT
    'demo_auditor',
    'ac0e7d037817094e9e0b4441f9bae3209d67b02fa484917065f71b16109a1a78',
    '审计演示账号',
    '+55 11 4002-2026',
    'audit.demo@portabrasil.local',
    1,
    '2026-04-20 09:00:00',
    '2026-05-08 16:20:00'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'demo_auditor');

INSERT INTO user_role (user_id, role_id)
SELECT u.id, r.id
FROM users u, roles r
WHERE u.username = 'demo_auditor'
  AND r.role_code = 'CUSTOMS'
  AND NOT EXISTS (
      SELECT 1 FROM user_role ur WHERE ur.user_id = u.id AND ur.role_id = r.id
  );

INSERT INTO user_role (user_id, role_id)
SELECT u.id, r.id
FROM users u, roles r
WHERE u.username = 'demo_auditor'
  AND r.role_code = 'FINANCE'
  AND NOT EXISTS (
      SELECT 1 FROM user_role ur WHERE ur.user_id = u.id AND ur.role_id = r.id
  );

-- Source PDF files and parse tasks -----------------------------------------
INSERT INTO pdf_file (file_name, file_path, file_size, file_hash, page_count, parse_status, upload_time, remark)
SELECT 'demo_invoice_santos_001.pdf', 'uploads/demo/demo_invoice_santos_001.pdf', 638420, 'demo_hash_santos_001', 5, 'SUCCESS', '2026-04-21 10:15:00', '演示数据：Santos进口清关单据'
WHERE NOT EXISTS (SELECT 1 FROM pdf_file WHERE file_hash = 'demo_hash_santos_001');

INSERT INTO pdf_file (file_name, file_path, file_size, file_hash, page_count, parse_status, upload_time, remark)
SELECT 'demo_invoice_itajai_002.pdf', 'uploads/demo/demo_invoice_itajai_002.pdf', 712884, 'demo_hash_itajai_002', 4, 'SUCCESS', '2026-04-25 14:22:00', '演示数据：Itajai进口清关单据'
WHERE NOT EXISTS (SELECT 1 FROM pdf_file WHERE file_hash = 'demo_hash_itajai_002');

INSERT INTO pdf_file (file_name, file_path, file_size, file_hash, page_count, parse_status, upload_time, remark)
SELECT 'demo_export_paranagua_003.pdf', 'uploads/demo/demo_export_paranagua_003.pdf', 522910, 'demo_hash_paranagua_003', 3, 'SUCCESS', '2026-04-28 11:06:00', '演示数据：Paranagua出口单据'
WHERE NOT EXISTS (SELECT 1 FROM pdf_file WHERE file_hash = 'demo_hash_paranagua_003');

INSERT INTO pdf_parse_task (file_id, task_no, parser_type, status, start_time, end_time, raw_result, created_time, updated_time)
SELECT id, 'TASK-DEMO-20260421-001', 'LLM', 'SUCCESS', '2026-04-21 10:15:12', '2026-04-21 10:16:08', '{"s_ref":"S/2026-IMP-001","status":"parsed"}', '2026-04-21 10:15:12', '2026-04-21 10:16:08'
FROM pdf_file
WHERE file_hash = 'demo_hash_santos_001'
  AND NOT EXISTS (SELECT 1 FROM pdf_parse_task WHERE task_no = 'TASK-DEMO-20260421-001');

INSERT INTO pdf_parse_task (file_id, task_no, parser_type, status, start_time, end_time, raw_result, created_time, updated_time)
SELECT id, 'TASK-DEMO-20260425-002', 'LLM', 'SUCCESS', '2026-04-25 14:22:10', '2026-04-25 14:23:02', '{"s_ref":"S/2026-IMP-002","status":"parsed"}', '2026-04-25 14:22:10', '2026-04-25 14:23:02'
FROM pdf_file
WHERE file_hash = 'demo_hash_itajai_002'
  AND NOT EXISTS (SELECT 1 FROM pdf_parse_task WHERE task_no = 'TASK-DEMO-20260425-002');

INSERT INTO pdf_parse_task (file_id, task_no, parser_type, status, start_time, end_time, raw_result, created_time, updated_time)
SELECT id, 'TASK-DEMO-20260428-003', 'LLM', 'SUCCESS', '2026-04-28 11:06:19', '2026-04-28 11:06:54', '{"s_ref":"S/2026-EXP-003","status":"parsed"}', '2026-04-28 11:06:19', '2026-04-28 11:06:54'
FROM pdf_file
WHERE file_hash = 'demo_hash_paranagua_003'
  AND NOT EXISTS (SELECT 1 FROM pdf_parse_task WHERE task_no = 'TASK-DEMO-20260428-003');

-- Customs business records --------------------------------------------------
INSERT INTO customs_business (
    s_ref, n_ref, document_no, invoice_no, nf_no, process_no, business_type,
    trade_company, customer_name, customer_address, customer_city, customer_state,
    customer_zip_code, customer_tax_no, issuer_name, issuer_tax_no, mawb_mbl,
    hawb_hbl, di_duimp_due, registration_date, arrival_date, customs_clearance_date,
    loading_date, destination, vessel_flight_name, gross_weight, volume_count,
    cargo_desc, freight_currency, freight_amount, fob_currency, fob_amount,
    cif_currency, cif_amount, cif_brl_amount, dollar_rate, euro_rate,
    total_credit, total_debit, balance_amount, balance_direction,
    source_file_id, source_page_no, data_status, created_time, updated_time
)
SELECT
    'S/2026-IMP-001', 'N/BR-2026-00418', 'DEM-2026-0418', 'INV-CN-20418', 'NF-904188',
    'PROC-SSZ-260418', 'IMPORT', 'Shenzhen Nova Machinery Co., Ltd.',
    'Alfa Auto Pecas Ltda.', 'Av. Paulista 1100', 'Sao Paulo', 'SP', '01310-100',
    '12.345.678/0001-90', 'PortaBrasil Logistica Ltda.', '41.222.333/0001-44',
    'MAWB-7845120091', 'HBL-SZX-260418-A', '26BR00041891-7',
    '2026-04-18', '2026-04-21', '2026-04-27', '2026-04-28',
    'Campinas Distribution Center', 'MSC ARIANE', '12840.500', 42,
    'CNC machining centers and spare parts', 'USD', '6200.00', 'USD', '84200.00',
    'USD', '90400.00', '463028.80', '5.122000', '5.530000',
    '184260.00', '184260.00', '0.00', 'BALANCED',
    (SELECT id FROM pdf_file WHERE file_hash = 'demo_hash_santos_001'),
    2, 'CONFIRMED', '2026-04-21 10:16:30', '2026-05-06 15:12:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_business WHERE s_ref = 'S/2026-IMP-001');

INSERT INTO customs_business (
    s_ref, n_ref, document_no, invoice_no, nf_no, process_no, business_type,
    trade_company, customer_name, customer_address, customer_city, customer_state,
    customer_zip_code, customer_tax_no, issuer_name, issuer_tax_no, mawb_mbl,
    hawb_hbl, di_duimp_due, registration_date, arrival_date, customs_clearance_date,
    loading_date, destination, vessel_flight_name, gross_weight, volume_count,
    cargo_desc, freight_currency, freight_amount, fob_currency, fob_amount,
    cif_currency, cif_amount, cif_brl_amount, dollar_rate, euro_rate,
    total_credit, total_debit, balance_amount, balance_direction,
    source_file_id, source_page_no, data_status, created_time, updated_time
)
SELECT
    'S/2026-IMP-002', 'N/BR-2026-00452', 'DEM-2026-0452', 'INV-HK-20452', 'NF-904529',
    'PROC-ITJ-260452', 'IMPORT', 'Guangzhou MedSupply Export Ltd.',
    'BioSaude Equipamentos Medicos SA', 'Rua XV de Novembro 245', 'Curitiba', 'PR', '80020-310',
    '28.774.119/0001-65', 'PortaBrasil Logistica Ltda.', '41.222.333/0001-44',
    'MBL-ITJ-88924512', 'HBL-CAN-260452-B', '26BR00045232-1',
    '2026-04-22', '2026-04-25', NULL, NULL,
    'Curitiba Warehouse', 'EVER LEADER', '6840.000', 28,
    'Sterile medical consumables and diagnostic kits', 'USD', '3900.00', 'USD', '51600.00',
    'USD', '55500.00', '284493.00', '5.126000', '5.541000',
    '103850.00', '105430.00', '1580.00', 'PAYABLE',
    (SELECT id FROM pdf_file WHERE file_hash = 'demo_hash_itajai_002'),
    1, 'REVIEWING', '2026-04-25 14:24:00', '2026-05-08 09:35:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_business WHERE s_ref = 'S/2026-IMP-002');

INSERT INTO customs_business (
    s_ref, n_ref, document_no, invoice_no, nf_no, process_no, business_type,
    trade_company, customer_name, customer_address, customer_city, customer_state,
    customer_zip_code, customer_tax_no, issuer_name, issuer_tax_no, mawb_mbl,
    hawb_hbl, di_duimp_due, registration_date, arrival_date, customs_clearance_date,
    loading_date, destination, vessel_flight_name, gross_weight, volume_count,
    cargo_desc, freight_currency, freight_amount, fob_currency, fob_amount,
    cif_currency, cif_amount, cif_brl_amount, dollar_rate, euro_rate,
    total_credit, total_debit, balance_amount, balance_direction,
    source_file_id, source_page_no, data_status, created_time, updated_time
)
SELECT
    'S/2026-EXP-003', 'N/BR-2026-00470', 'DEM-2026-0470', 'EXP-BR-20470', 'NF-EXP-0470',
    'PROC-PNG-260470', 'EXPORT', 'Cafe Serra Alta Exportadora Ltda.',
    'Lusitania Foods Importacao Lda.', 'Rua do Comercio 88', 'Lisbon', 'LX', '1100-150',
    'PT-509772118', 'PortaBrasil Logistica Ltda.', '41.222.333/0001-44',
    'MBL-PNG-55210490', 'HBL-PNG-260470-C', '26BRDUE047000-3',
    '2026-04-27', '2026-04-28', '2026-05-02', '2026-05-04',
    'Port of Lisbon', 'MAERSK LIMA', '22000.000', 310,
    'Roasted coffee beans', 'USD', '4800.00', 'USD', '73500.00',
    'USD', '78300.00', '401615.60', '5.129000', '5.548000',
    '76840.00', '76840.00', '0.00', 'BALANCED',
    (SELECT id FROM pdf_file WHERE file_hash = 'demo_hash_paranagua_003'),
    1, 'CONFIRMED', '2026-04-28 11:07:20', '2026-05-05 13:41:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_business WHERE s_ref = 'S/2026-EXP-003');

INSERT INTO customs_business (
    s_ref, n_ref, document_no, invoice_no, nf_no, process_no, business_type,
    trade_company, customer_name, customer_city, customer_state, customer_tax_no,
    issuer_name, issuer_tax_no, mawb_mbl, hawb_hbl, di_duimp_due, registration_date,
    arrival_date, customs_clearance_date, destination, vessel_flight_name, gross_weight,
    volume_count, cargo_desc, freight_currency, freight_amount, fob_currency, fob_amount,
    cif_currency, cif_amount, cif_brl_amount, dollar_rate, total_credit, total_debit,
    balance_amount, balance_direction, data_status, created_time, updated_time
)
SELECT
    'S/2026-IMP-004', 'N/BR-2026-00491', 'DEM-2026-0491', 'INV-KR-20491', 'NF-904911',
    'PROC-GIG-260491', 'IMPORT', 'Busan Smart Components Inc.',
    'Energia Solar Nordeste Ltda.', 'Recife', 'PE', '33.908.221/0001-02',
    'PortaBrasil Logistica Ltda.', '41.222.333/0001-44', 'AWB-988220412', 'HAWB-ICN-260491-D',
    '26BR00049187-0', '2026-04-30', '2026-05-03', NULL, 'Recife Solar Plant',
    'KE Cargo 273', '3420.750', 16, 'Photovoltaic inverters and connectors',
    'USD', '2600.00', 'USD', '41750.00', 'USD', '44350.00', '227496.80',
    '5.130000', '94820.00', '92040.00', '2780.00', 'FAVOR',
    'REVIEWING', '2026-05-03 08:45:00', '2026-05-09 10:22:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_business WHERE s_ref = 'S/2026-IMP-004');

INSERT INTO customs_business (
    s_ref, n_ref, document_no, invoice_no, nf_no, process_no, business_type,
    trade_company, customer_name, customer_city, customer_state, customer_tax_no,
    issuer_name, issuer_tax_no, mawb_mbl, hawb_hbl, di_duimp_due, registration_date,
    arrival_date, customs_clearance_date, destination, vessel_flight_name, gross_weight,
    volume_count, cargo_desc, freight_currency, freight_amount, fob_currency, fob_amount,
    cif_currency, cif_amount, cif_brl_amount, dollar_rate, total_credit, total_debit,
    balance_amount, balance_direction, data_status, created_time, updated_time
)
SELECT
    'S/2026-IMP-005', 'N/BR-2026-00508', 'DEM-2026-0508', 'INV-US-20508', 'NF-905081',
    'PROC-VCP-260508', 'IMPORT', 'Austin Lab Instruments LLC',
    'Laboratorio Atlantico SA', 'Sao Paulo', 'SP', '77.512.019/0001-73',
    'PortaBrasil Logistica Ltda.', '41.222.333/0001-44', 'AWB-045988721', 'HAWB-DFW-260508-E',
    '26BR00050811-5', '2026-05-04', '2026-05-05', '2026-05-09', 'Sao Paulo Lab Hub',
    'AA Cargo 963', '920.300', 9, 'Laboratory spectrometers',
    'USD', '1850.00', 'USD', '36800.00', 'USD', '38650.00', '198351.80',
    '5.132000', '64510.00', '64510.00', '0.00', 'BALANCED',
    'CONFIRMED', '2026-05-05 11:50:00', '2026-05-09 14:10:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_business WHERE s_ref = 'S/2026-IMP-005');

-- Fee items -----------------------------------------------------------------
INSERT INTO customs_business_fee_item (business_id, fee_date, fee_code, fee_name, credit_amount, debit_amount, line_no, raw_text)
SELECT b.id, f.fee_date, f.fee_code, f.fee_name, f.credit_amount, f.debit_amount, f.line_no, f.raw_text
FROM customs_business b
JOIN (
    SELECT 'S/2026-IMP-001' AS s_ref, '2026-04-22' AS fee_date, 'II' AS fee_code, 'Import Duty' AS fee_name, '72240.00' AS credit_amount, NULL AS debit_amount, 1 AS line_no, 'II Import Duty 72,240.00' AS raw_text
    UNION ALL SELECT 'S/2026-IMP-001', '2026-04-22', 'IPI', 'Industrialized Product Tax', '23560.00', NULL, 2, 'IPI 23,560.00'
    UNION ALL SELECT 'S/2026-IMP-001', '2026-04-23', 'PIS', 'PIS Import', '8180.00', NULL, 3, 'PIS Import 8,180.00'
    UNION ALL SELECT 'S/2026-IMP-001', '2026-04-23', 'COFINS', 'COFINS Import', '37620.00', NULL, 4, 'COFINS 37,620.00'
    UNION ALL SELECT 'S/2026-IMP-001', '2026-04-25', 'ICMS', 'ICMS Sao Paulo', '42660.00', NULL, 5, 'ICMS 42,660.00'
    UNION ALL SELECT 'S/2026-IMP-002', '2026-04-26', 'II', 'Import Duty', '42120.00', NULL, 1, 'II Import Duty 42,120.00'
    UNION ALL SELECT 'S/2026-IMP-002', '2026-04-26', 'IPI', 'Industrialized Product Tax', '11850.00', NULL, 2, 'IPI 11,850.00'
    UNION ALL SELECT 'S/2026-IMP-002', '2026-04-27', 'PIS', 'PIS Import', '5230.00', NULL, 3, 'PIS 5,230.00'
    UNION ALL SELECT 'S/2026-IMP-002', '2026-04-27', 'COFINS', 'COFINS Import', '24090.00', NULL, 4, 'COFINS 24,090.00'
    UNION ALL SELECT 'S/2026-IMP-002', '2026-04-28', 'ICMS', 'ICMS Parana', '18960.00', NULL, 5, 'ICMS 18,960.00'
    UNION ALL SELECT 'S/2026-IMP-002', '2026-04-29', 'STORAGE', 'Terminal Storage', NULL, '3180.00', 6, 'Storage 3,180.00 debit'
    UNION ALL SELECT 'S/2026-EXP-003', '2026-04-29', 'DOC', 'Export Documentation Fee', '12840.00', NULL, 1, 'Export doc fee 12,840.00'
    UNION ALL SELECT 'S/2026-EXP-003', '2026-04-29', 'THC', 'Terminal Handling Charge', '28800.00', NULL, 2, 'THC 28,800.00'
    UNION ALL SELECT 'S/2026-EXP-003', '2026-05-01', 'FREIGHT', 'Ocean Freight Recharge', '35200.00', NULL, 3, 'Freight recharge 35,200.00'
    UNION ALL SELECT 'S/2026-IMP-004', '2026-05-04', 'II', 'Import Duty', '39210.00', NULL, 1, 'II 39,210.00'
    UNION ALL SELECT 'S/2026-IMP-004', '2026-05-04', 'IPI', 'Industrialized Product Tax', '9540.00', NULL, 2, 'IPI 9,540.00'
    UNION ALL SELECT 'S/2026-IMP-004', '2026-05-05', 'PIS', 'PIS Import', '4180.00', NULL, 3, 'PIS 4,180.00'
    UNION ALL SELECT 'S/2026-IMP-004', '2026-05-05', 'COFINS', 'COFINS Import', '19240.00', NULL, 4, 'COFINS 19,240.00'
    UNION ALL SELECT 'S/2026-IMP-004', '2026-05-06', 'ICMS', 'ICMS Pernambuco', '19870.00', NULL, 5, 'ICMS 19,870.00'
    UNION ALL SELECT 'S/2026-IMP-005', '2026-05-05', 'II', 'Import Duty', '22040.00', NULL, 1, 'II 22,040.00'
    UNION ALL SELECT 'S/2026-IMP-005', '2026-05-06', 'IPI', 'Industrialized Product Tax', '8120.00', NULL, 2, 'IPI 8,120.00'
    UNION ALL SELECT 'S/2026-IMP-005', '2026-05-06', 'PIS', 'PIS Import', '3660.00', NULL, 3, 'PIS 3,660.00'
    UNION ALL SELECT 'S/2026-IMP-005', '2026-05-07', 'COFINS', 'COFINS Import', '16840.00', NULL, 4, 'COFINS 16,840.00'
    UNION ALL SELECT 'S/2026-IMP-005', '2026-05-07', 'ICMS', 'ICMS Sao Paulo', '13850.00', NULL, 5, 'ICMS 13,850.00'
) f ON f.s_ref = b.s_ref
WHERE NOT EXISTS (
    SELECT 1 FROM customs_business_fee_item existing
    WHERE existing.business_id = b.id AND existing.line_no = f.line_no AND existing.fee_code = f.fee_code
);

-- Process tracking ----------------------------------------------------------
INSERT INTO customs_process_record (business_id, bl_no, goods_desc, declaration_date, port_name, overall_status, created_time, updated_time)
SELECT (SELECT id FROM customs_business WHERE s_ref = 'S/2026-IMP-001'), 'BL-DEMO-SSZ-001', 'CNC machining centers and spare parts', '2026-04-22', 'Santos (SSZ)', 'CLEARED', '2026-04-21 10:30:00', '2026-04-28 16:45:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_process_record WHERE bl_no = 'BL-DEMO-SSZ-001');

INSERT INTO customs_process_record (business_id, bl_no, goods_desc, declaration_date, port_name, overall_status, created_time, updated_time)
SELECT (SELECT id FROM customs_business WHERE s_ref = 'S/2026-IMP-002'), 'BL-DEMO-ITJ-002', 'Sterile medical consumables and diagnostic kits', '2026-04-26', 'Itajai (ITJ)', 'INSPECTION', '2026-04-25 14:40:00', '2026-05-08 09:50:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_process_record WHERE bl_no = 'BL-DEMO-ITJ-002');

INSERT INTO customs_process_record (business_id, bl_no, goods_desc, declaration_date, port_name, overall_status, created_time, updated_time)
SELECT (SELECT id FROM customs_business WHERE s_ref = 'S/2026-EXP-003'), 'BL-DEMO-PNG-003', 'Roasted coffee beans', '2026-04-29', 'Paranagua (PNG)', 'CLEARED', '2026-04-28 11:20:00', '2026-05-04 18:05:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_process_record WHERE bl_no = 'BL-DEMO-PNG-003');

INSERT INTO customs_process_record (business_id, bl_no, goods_desc, declaration_date, port_name, overall_status, created_time, updated_time)
SELECT (SELECT id FROM customs_business WHERE s_ref = 'S/2026-IMP-004'), 'BL-DEMO-GIG-004', 'Photovoltaic inverters and connectors', '2026-05-04', 'Rio de Janeiro (GIG)', 'PROCESSING', '2026-05-03 09:00:00', '2026-05-09 10:45:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_process_record WHERE bl_no = 'BL-DEMO-GIG-004');

INSERT INTO customs_process_record (business_id, bl_no, goods_desc, declaration_date, port_name, overall_status, created_time, updated_time)
SELECT (SELECT id FROM customs_business WHERE s_ref = 'S/2026-IMP-005'), 'BL-DEMO-VCP-005', 'Laboratory spectrometers', '2026-05-05', 'Viracopos (VCP)', 'CLEARED', '2026-05-05 12:10:00', '2026-05-09 14:20:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_process_record WHERE bl_no = 'BL-DEMO-VCP-005');

INSERT INTO customs_process_step (process_id, step_no, status, completion_time, step_desc)
SELECT p.id, s.step_no,
    CASE
        WHEN p.overall_status = 'CLEARED' THEN 'COMPLETE'
        WHEN p.overall_status = 'INSPECTION' AND s.step_no <= 6 THEN 'COMPLETE'
        WHEN p.overall_status = 'PROCESSING' AND s.step_no <= 4 THEN 'COMPLETE'
        ELSE 'PENDING'
    END,
    CASE
        WHEN p.overall_status = 'CLEARED' OR (p.overall_status = 'INSPECTION' AND s.step_no <= 6) OR (p.overall_status = 'PROCESSING' AND s.step_no <= 4)
        THEN CASE s.step_no
            WHEN 1 THEN '05-01 09:00'
            WHEN 2 THEN '05-01 14:00'
            WHEN 3 THEN '05-02 10:30'
            WHEN 4 THEN '05-03 11:20'
            WHEN 5 THEN '05-04 15:40'
            WHEN 6 THEN '05-05 10:10'
            WHEN 7 THEN '05-06 16:25'
            WHEN 8 THEN '05-07 09:35'
            WHEN 9 THEN '05-08 13:50'
            ELSE '05-09 17:10'
        END
        ELSE NULL
    END,
    CASE s.step_no
        WHEN 1 THEN '单据接收'
        WHEN 2 THEN '商业发票校验'
        WHEN 3 THEN '装箱单校验'
        WHEN 4 THEN '税费预估'
        WHEN 5 THEN '申报提交'
        WHEN 6 THEN '海关通道判定'
        WHEN 7 THEN '税费支付'
        WHEN 8 THEN '海关放行'
        WHEN 9 THEN '提货安排'
        ELSE '归档完成'
    END
FROM customs_process_record p
JOIN (
    SELECT 1 AS step_no UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
    UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10
) s
WHERE p.bl_no IN ('BL-DEMO-SSZ-001', 'BL-DEMO-ITJ-002', 'BL-DEMO-PNG-003', 'BL-DEMO-GIG-004', 'BL-DEMO-VCP-005')
  AND NOT EXISTS (
      SELECT 1 FROM customs_process_step existing
      WHERE existing.process_id = p.id AND existing.step_no = s.step_no
  );

INSERT INTO customs_activity (activity_type, title, description, related_process_id, occurred_at)
SELECT 'SUCCESS', '审计完成：S/2026-IMP-001', '规则审计未发现金额异常，可作为正常案例展示。', (SELECT id FROM customs_process_record WHERE bl_no = 'BL-DEMO-SSZ-001'), '2026-05-06 15:15:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_activity WHERE title = '审计完成：S/2026-IMP-001');

INSERT INTO customs_activity (activity_type, title, description, related_process_id, occurred_at)
SELECT 'ALERT', '审计预警：S/2026-IMP-002', '费用合计与业务借贷总额存在差异，建议财务复核。', (SELECT id FROM customs_process_record WHERE bl_no = 'BL-DEMO-ITJ-002'), '2026-05-08 09:58:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_activity WHERE title = '审计预警：S/2026-IMP-002');

INSERT INTO customs_activity (activity_type, title, description, related_process_id, occurred_at)
SELECT 'INFO', '流程推进：S/2026-IMP-004', '新能源设备仍在申报处理中，等待税费支付确认。', (SELECT id FROM customs_process_record WHERE bl_no = 'BL-DEMO-GIG-004'), '2026-05-09 10:50:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_activity WHERE title = '流程推进：S/2026-IMP-004');

-- Cost analysis records -----------------------------------------------------
INSERT INTO fx_rate_cache (base_currency, quote_currency, rate, source, updated_at)
SELECT 'USD', 'BRL', '5.1320', 'demo_seed', '2026-05-09 09:00:00'
WHERE NOT EXISTS (SELECT 1 FROM fx_rate_cache WHERE base_currency = 'USD' AND quote_currency = 'BRL');

INSERT INTO customs_cost_record (
    process_record_id, record_no, customs_fee, refund_fee, usd_amount, usd_rate,
    other_fees, total_qty, total_base, per_unit_cost, currency, note, created_by,
    created_time, updated_time
)
SELECT (SELECT id FROM customs_process_record WHERE bl_no = 'BL-DEMO-SSZ-001'), 'COST-DEMO-20260428-001',
       '184260.0000', '0.0000', '6200.0000', '5.122000', '2800.0000',
       '420.0000', '218826.4000', '521.0152', 'BRL',
       '演示：正常审计案例，业务费用与成本记录一致', (SELECT id FROM users WHERE username = 'demo_auditor'),
       '2026-04-28 17:05:00', '2026-05-06 15:10:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_cost_record WHERE record_no = 'COST-DEMO-20260428-001');

INSERT INTO customs_cost_record (
    process_record_id, record_no, customs_fee, refund_fee, usd_amount, usd_rate,
    other_fees, total_qty, total_base, per_unit_cost, currency, note, created_by,
    created_time, updated_time
)
SELECT (SELECT id FROM customs_process_record WHERE bl_no = 'BL-DEMO-ITJ-002'), 'COST-DEMO-20260508-002',
       '105430.0000', '0.0000', '3900.0000', '5.126000', '5200.0000',
       '2800.0000', '130621.4000', '46.6505', 'BRL',
       '演示：查验与费用差异案例，适合展示审计发现项', (SELECT id FROM users WHERE username = 'demo_auditor'),
       '2026-05-08 09:40:00', '2026-05-08 10:05:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_cost_record WHERE record_no = 'COST-DEMO-20260508-002');

INSERT INTO customs_cost_record (
    process_record_id, record_no, customs_fee, refund_fee, usd_amount, usd_rate,
    other_fees, total_qty, total_base, per_unit_cost, currency, note, created_by,
    created_time, updated_time
)
SELECT (SELECT id FROM customs_process_record WHERE bl_no = 'BL-DEMO-GIG-004'), 'COST-DEMO-20260509-004',
       '92040.0000', '2780.0000', '2600.0000', '5.130000', '4600.0000',
       '160.0000', '107198.0000', '669.9875', 'BRL',
       '演示：客户应收余额为 FAVOR，需确认是否退款或抵扣', (SELECT id FROM users WHERE username = 'demo_auditor'),
       '2026-05-09 10:30:00', '2026-05-09 10:40:00'
WHERE NOT EXISTS (SELECT 1 FROM customs_cost_record WHERE record_no = 'COST-DEMO-20260509-004');

INSERT INTO customs_cost_item (cost_record_id, line_no, product_name, qty, allocation_cost, unit_cost)
SELECT c.id, i.line_no, i.product_name, i.qty, i.allocation_cost, i.unit_cost
FROM customs_cost_record c
JOIN (
    SELECT 'COST-DEMO-20260428-001' AS record_no, 1 AS line_no, 'CNC main spindle assembly' AS product_name, '120.0000' AS qty, '62521.8240' AS allocation_cost, '521.0152' AS unit_cost
    UNION ALL SELECT 'COST-DEMO-20260428-001', 2, 'Servo drive unit', '180.0000', '93782.7360', '521.0152'
    UNION ALL SELECT 'COST-DEMO-20260428-001', 3, 'Precision tooling kit', '120.0000', '62521.8240', '521.0152'
    UNION ALL SELECT 'COST-DEMO-20260508-002', 1, 'Diagnostic reagent kit', '1500.0000', '69975.7500', '46.6505'
    UNION ALL SELECT 'COST-DEMO-20260508-002', 2, 'Sterile syringe pack', '1300.0000', '60645.6500', '46.6505'
    UNION ALL SELECT 'COST-DEMO-20260509-004', 1, 'Solar inverter module', '80.0000', '53599.0000', '669.9875'
    UNION ALL SELECT 'COST-DEMO-20260509-004', 2, 'MC4 connector set', '80.0000', '53599.0000', '669.9875'
) i ON i.record_no = c.record_no
WHERE NOT EXISTS (
    SELECT 1 FROM customs_cost_item existing
    WHERE existing.cost_record_id = c.id AND existing.line_no = i.line_no
);

-- AI audit runs and findings ------------------------------------------------
INSERT INTO ai_audit_run (
    business_id, cost_record_id, source, model_name, status, risk_level, score,
    summary, checks_json, input_json, raw_output, error_message, created_by,
    created_time, updated_time
)
SELECT
    (SELECT id FROM customs_business WHERE s_ref = 'S/2026-IMP-001'),
    (SELECT id FROM customs_cost_record WHERE record_no = 'COST-DEMO-20260428-001'),
    'RULE', NULL, 'SUCCESS', 'LOW', 94.00,
    '规则审计完成：业务借贷平衡，费用明细合计与成本记录一致，未发现重大风险。',
    '[{"code":"BALANCE_CHECK","name":"借贷平衡","status":"PASS"},{"code":"FEE_TOTAL_CHECK","name":"费用合计一致性","status":"PASS"},{"code":"COST_TRACE_CHECK","name":"成本记录追踪","status":"PASS"}]',
    '{"business_ref":"S/2026-IMP-001","cost_record_no":"COST-DEMO-20260428-001"}',
    '{"risk_level":"LOW","score":94,"findings":[]}',
    NULL,
    (SELECT id FROM users WHERE username = 'demo_auditor'),
    '2026-05-06 15:12:00', '2026-05-06 15:12:08'
WHERE NOT EXISTS (
    SELECT 1 FROM ai_audit_run WHERE business_id = (SELECT id FROM customs_business WHERE s_ref = 'S/2026-IMP-001')
);

INSERT INTO ai_audit_run (
    business_id, cost_record_id, source, model_name, status, risk_level, score,
    summary, checks_json, input_json, raw_output, error_message, created_by,
    created_time, updated_time
)
SELECT
    (SELECT id FROM customs_business WHERE s_ref = 'S/2026-IMP-002'),
    (SELECT id FROM customs_cost_record WHERE record_no = 'COST-DEMO-20260508-002'),
    'RULE', NULL, 'SUCCESS', 'HIGH', 62.00,
    '规则审计完成：发现借贷差异、查验状态下仓储费用偏高、成本记录缺少退款说明。',
    '[{"code":"BALANCE_CHECK","name":"借贷平衡","status":"WARN"},{"code":"FEE_TOTAL_CHECK","name":"费用合计一致性","status":"FAIL"},{"code":"INSPECTION_STORAGE_CHECK","name":"查验仓储费用","status":"WARN"}]',
    '{"business_ref":"S/2026-IMP-002","cost_record_no":"COST-DEMO-20260508-002"}',
    '{"risk_level":"HIGH","score":62,"finding_count":3}',
    NULL,
    (SELECT id FROM users WHERE username = 'demo_auditor'),
    '2026-05-08 09:55:00', '2026-05-08 09:55:12'
WHERE NOT EXISTS (
    SELECT 1 FROM ai_audit_run WHERE business_id = (SELECT id FROM customs_business WHERE s_ref = 'S/2026-IMP-002')
);

INSERT INTO ai_audit_run (
    business_id, cost_record_id, source, model_name, status, risk_level, score,
    summary, checks_json, input_json, raw_output, error_message, created_by,
    created_time, updated_time
)
SELECT
    (SELECT id FROM customs_business WHERE s_ref = 'S/2026-IMP-004'),
    (SELECT id FROM customs_cost_record WHERE record_no = 'COST-DEMO-20260509-004'),
    'RULE', NULL, 'SUCCESS', 'MEDIUM', 76.00,
    '规则审计完成：客户余额方向为 FAVOR，建议确认退款、抵扣或后续账期处理。',
    '[{"code":"BALANCE_DIRECTION_CHECK","name":"余额方向","status":"WARN"},{"code":"REFUND_TRACE_CHECK","name":"退款追踪","status":"WARN"},{"code":"FIELD_COMPLETENESS_CHECK","name":"关键字段完整性","status":"PASS"}]',
    '{"business_ref":"S/2026-IMP-004","cost_record_no":"COST-DEMO-20260509-004"}',
    '{"risk_level":"MEDIUM","score":76,"finding_count":2}',
    NULL,
    (SELECT id FROM users WHERE username = 'demo_auditor'),
    '2026-05-09 10:42:00', '2026-05-09 10:42:11'
WHERE NOT EXISTS (
    SELECT 1 FROM ai_audit_run WHERE business_id = (SELECT id FROM customs_business WHERE s_ref = 'S/2026-IMP-004')
);

INSERT INTO ai_audit_finding (
    audit_run_id, finding_type, severity, rule_code, title, description, evidence, suggestion, amount, created_time
)
SELECT r.id, f.finding_type, f.severity, f.rule_code, f.title, f.description, f.evidence, f.suggestion, f.amount, f.created_time
FROM ai_audit_run r
JOIN customs_business b ON b.id = r.business_id
JOIN (
    SELECT 'S/2026-IMP-002' AS s_ref, 'RISK' AS finding_type, 'HIGH' AS severity, 'BALANCE_MISMATCH' AS rule_code,
           '借贷余额不一致' AS title,
           '业务主表显示借方高于贷方，余额方向为 PAYABLE，需要确认是否仍有未入账费用或付款差额。' AS description,
           'total_credit=103850.00, total_debit=105430.00, balance_amount=1580.00' AS evidence,
           '请核对付款凭证、终端收费单与客户应付通知，确认 1,580.00 BRL 差额来源。' AS suggestion,
           '1580.0000' AS amount, '2026-05-08 09:55:13' AS created_time
    UNION ALL SELECT 'S/2026-IMP-002', 'RISK', 'MEDIUM', 'FEE_SUM_MISMATCH',
           '费用明细与业务总额存在差异',
           '费用明细贷方合计为 102,250.00 BRL，业务贷方为 103,850.00 BRL，存在 1,600.00 BRL 未解释差异。',
           'fee_credit_sum=102250.00, business_total_credit=103850.00',
           '补充缺失费用行或调整业务总额后重新执行审计。',
           '1600.0000', '2026-05-08 09:55:13'
    UNION ALL SELECT 'S/2026-IMP-002', 'WARNING', 'MEDIUM', 'INSPECTION_STORAGE',
           '查验状态下仓储费用偏高',
           '该流程处于 INSPECTION，且存在 3,180.00 BRL 仓储借方费用，可能影响客户结算。',
           'overall_status=INSPECTION, storage_debit=3180.00',
           '向报关员确认查验时长和终端账单，必要时在成本备注中说明。',
           '3180.0000', '2026-05-08 09:55:13'
    UNION ALL SELECT 'S/2026-IMP-004', 'WARNING', 'MEDIUM', 'BALANCE_FAVOR',
           '客户余额为 FAVOR',
           '业务记录显示客户方向为 FAVOR，可能需要退款、抵扣或转入后续账期。',
           'balance_direction=FAVOR, balance_amount=2780.00',
           '和财务确认 2,780.00 BRL 的处理方式，并在回款记录中留痕。',
           '2780.0000', '2026-05-09 10:42:12'
    UNION ALL SELECT 'S/2026-IMP-004', 'RISK', 'LOW', 'CLEARANCE_PENDING',
           '清关日期尚未填写',
           '业务仍处于 REVIEWING，清关日期为空，后续统计报表可能无法准确计算清关周期。',
           'customs_clearance_date=NULL, data_status=REVIEWING',
           '放行后及时补录清关日期，并重新生成流程报表。',
           NULL, '2026-05-09 10:42:12'
) f ON f.s_ref = b.s_ref
WHERE NOT EXISTS (
    SELECT 1 FROM ai_audit_finding existing
    WHERE existing.audit_run_id = r.id AND existing.rule_code = f.rule_code
);

-- AI finance reviews --------------------------------------------------------
INSERT INTO ai_finance_review (
    cost_record_id, source, model_name, status, health_level, score, summary,
    metrics_json, input_json, raw_output, error_message, created_by, created_time, updated_time
)
SELECT
    (SELECT id FROM customs_cost_record WHERE record_no = 'COST-DEMO-20260428-001'),
    'RULE', NULL, 'SUCCESS', 'HEALTHY', 91.00,
    '财务复核完成：单位成本稳定，成本构成清晰，可直接用于报价复盘。',
    '{"total_base":218826.40,"per_unit_cost":521.0152,"refund_ratio":0,"other_fee_ratio":0.0128}',
    '{"cost_record_no":"COST-DEMO-20260428-001"}',
    '{"health_level":"HEALTHY","score":91}',
    NULL,
    (SELECT id FROM users WHERE username = 'demo_auditor'),
    '2026-05-06 15:13:00', '2026-05-06 15:13:07'
WHERE NOT EXISTS (
    SELECT 1 FROM ai_finance_review WHERE cost_record_id = (SELECT id FROM customs_cost_record WHERE record_no = 'COST-DEMO-20260428-001')
);

INSERT INTO ai_finance_review (
    cost_record_id, source, model_name, status, health_level, score, summary,
    metrics_json, input_json, raw_output, error_message, created_by, created_time, updated_time
)
SELECT
    (SELECT id FROM customs_cost_record WHERE record_no = 'COST-DEMO-20260508-002'),
    'RULE', NULL, 'SUCCESS', 'WATCH', 68.00,
    '财务复核完成：查验导致仓储及其他费用占比偏高，建议单独向客户说明。',
    '{"total_base":130621.40,"per_unit_cost":46.6505,"other_fee_ratio":0.0398,"inspection_related_fee":3180}',
    '{"cost_record_no":"COST-DEMO-20260508-002"}',
    '{"health_level":"WATCH","score":68}',
    NULL,
    (SELECT id FROM users WHERE username = 'demo_auditor'),
    '2026-05-08 10:02:00', '2026-05-08 10:02:06'
WHERE NOT EXISTS (
    SELECT 1 FROM ai_finance_review WHERE cost_record_id = (SELECT id FROM customs_cost_record WHERE record_no = 'COST-DEMO-20260508-002')
);

INSERT INTO ai_finance_item (finance_review_id, severity, title, description, recommendation, created_time)
SELECT fr.id, i.severity, i.title, i.description, i.recommendation, i.created_time
FROM ai_finance_review fr
JOIN customs_cost_record c ON c.id = fr.cost_record_id
JOIN (
    SELECT 'COST-DEMO-20260508-002' AS record_no, 'MEDIUM' AS severity,
           '其他费用占比偏高' AS title,
           '其他费用 5,200.00 BRL 占总成本约 3.98%，高于常规演示阈值。' AS description,
           '在客户账单备注中拆分查验、仓储和终端服务费。' AS recommendation,
           '2026-05-08 10:02:07' AS created_time
    UNION ALL SELECT 'COST-DEMO-20260508-002', 'HIGH',
           '查验相关费用需补充凭证',
           '流程状态为 INSPECTION，成本记录中出现较高附加费用。',
           '上传终端仓储账单或在成本备注中写明凭证编号。',
           '2026-05-08 10:02:07'
) i ON i.record_no = c.record_no
WHERE NOT EXISTS (
    SELECT 1 FROM ai_finance_item existing
    WHERE existing.finance_review_id = fr.id AND existing.title = i.title
);

-- Statement summary ---------------------------------------------------------
INSERT INTO statement_summary (
    statement_no, issue_date, due_date, total_amount, amount_direction, customer_name,
    customer_address, customer_city, customer_state, customer_zip_code, customer_tax_no,
    issuer_name, created_time, updated_time
)
SELECT 'DEMO-0526-AUDIT', '2026-05-09', '2026-05-30', '352228.40', 'S/Favor',
       'Demo Audit Customer Group', 'Av. Brasil 2600', 'Sao Paulo', 'SP', '01430-001',
       '00.111.222/0001-88', 'PortaBrasil Logistica Ltda.', '2026-05-09 16:00:00', '2026-05-09 16:00:00'
WHERE NOT EXISTS (SELECT 1 FROM statement_summary WHERE statement_no = 'DEMO-0526-AUDIT');

INSERT INTO statement_summary_item (summary_id, n_ref, s_ref, nf_no, amount_direction, balance_amount, business_id, line_no)
SELECT ss.id, b.n_ref, b.s_ref, b.nf_no, b.balance_direction, b.balance_amount, b.id, x.line_no
FROM statement_summary ss
JOIN (
    SELECT 'S/2026-IMP-001' AS s_ref, 1 AS line_no
    UNION ALL SELECT 'S/2026-IMP-002', 2
    UNION ALL SELECT 'S/2026-IMP-004', 3
) x
JOIN customs_business b ON b.s_ref = x.s_ref
WHERE ss.statement_no = 'DEMO-0526-AUDIT'
  AND NOT EXISTS (
      SELECT 1 FROM statement_summary_item existing
      WHERE existing.summary_id = ss.id AND existing.s_ref = b.s_ref
  );

COMMIT;
