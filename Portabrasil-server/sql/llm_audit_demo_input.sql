-- PortaBrasil LLM audit demo input data.
--
-- This file inserts only audit input data: business records, fee items,
-- cost records, and cost items. It deliberately does NOT insert rows into
-- ai_audit_run or ai_audit_finding.
--
-- Demo flow:
--   1. Import this file.
--   2. Open /audit.
--   3. Run audits for:
--      business_id=11101, cost_record_id=11601  -- normal case
--      business_id=11102, cost_record_id=11602  -- high-risk case
--      business_id=11103, cost_record_id=11603  -- medium-risk case
--   4. The generated audit rows should show source=LLM when API key is active.

BEGIN;

INSERT INTO customs_business (
    id, s_ref, n_ref, document_no, invoice_no, nf_no, process_no, business_type,
    trade_company, customer_name, customer_city, customer_state, customer_tax_no,
    issuer_name, issuer_tax_no, mawb_mbl, hawb_hbl, di_duimp_due, registration_date,
    arrival_date, customs_clearance_date, loading_date, destination, vessel_flight_name,
    gross_weight, volume_count, cargo_desc, freight_currency, freight_amount,
    fob_currency, fob_amount, cif_currency, cif_amount, cif_brl_amount,
    dollar_rate, euro_rate, total_credit, total_debit, balance_amount,
    balance_direction, data_status, created_time, updated_time
) VALUES
(11101, 'LLM/2026-NORMAL-001', 'N/LLM-001', 'LLM-DEMO-001', 'INV-LLM-001', 'NF-LLM-001', 'PROC-LLM-001', 'IMPORT', 'Shenzhen Nova Machinery Co., Ltd.', 'Alfa Auto Pecas Ltda.', 'Sao Paulo', 'SP', '12.345.678/0001-90', 'PortaBrasil Logistica Ltda.', '41.222.333/0001-44', 'MAWB-LLM-001', 'HBL-LLM-001', '26BRLLM001-1', '2026-04-18', '2026-04-21', '2026-04-27', '2026-04-28', 'Campinas Distribution Center', 'MSC ARIANE', 12840.500, 42, 'CNC machining centers and spare parts', 'USD', 6200.00, 'USD', 84200.00, 'USD', 90400.00, 463028.80, 5.122000, 5.530000, 184260.00, 184260.00, 0.00, 'BALANCED', 'CONFIRMED', '2026-04-21 10:16:30', '2026-05-06 15:12:00'),
(11102, 'LLM/2026-RISK-002', 'N/LLM-002', 'LLM-DEMO-002', 'INV-LLM-002', 'NF-LLM-002', 'PROC-LLM-002', 'IMPORT', 'Guangzhou MedSupply Export Ltd.', 'BioSaude Equipamentos Medicos SA', 'Curitiba', 'PR', '28.774.119/0001-65', 'PortaBrasil Logistica Ltda.', '41.222.333/0001-44', 'MBL-LLM-002', 'HBL-LLM-002', '26BRLLM002-2', '2026-04-22', '2026-04-25', NULL, NULL, 'Curitiba Warehouse', 'EVER LEADER', 6840.000, 28, 'Sterile medical consumables and diagnostic kits', 'USD', 3900.00, 'USD', 51600.00, 'USD', 55500.00, 284493.00, 5.126000, 5.541000, 103850.00, 105430.00, 1580.00, 'PAYABLE', 'REVIEWING', '2026-04-25 14:24:00', '2026-05-08 09:35:00'),
(11103, 'LLM/2026-WATCH-003', 'N/LLM-003', 'LLM-DEMO-003', 'INV-LLM-003', 'NF-LLM-003', 'PROC-LLM-003', 'IMPORT', 'Busan Smart Components Inc.', 'Energia Solar Nordeste Ltda.', 'Recife', 'PE', '33.908.221/0001-02', 'PortaBrasil Logistica Ltda.', '41.222.333/0001-44', 'AWB-LLM-003', 'HAWB-LLM-003', '26BRLLM003-3', '2026-04-30', '2026-05-03', NULL, NULL, 'Recife Solar Plant', 'KE Cargo 273', 3420.750, 16, 'Photovoltaic inverters and connectors', 'USD', 2600.00, 'USD', 41750.00, 'USD', 44350.00, 227496.80, 5.130000, NULL, 94820.00, 92040.00, 2780.00, 'FAVOR', 'REVIEWING', '2026-05-03 08:45:00', '2026-05-09 10:22:00');

INSERT INTO customs_business_fee_item (id, business_id, fee_date, fee_code, fee_name, credit_amount, debit_amount, line_no, raw_text, created_time) VALUES
(11201, 11101, '2026-04-22', 'II', 'Import Duty', 72240.00, NULL, 1, 'II Import Duty 72,240.00', '2026-04-22 09:00:00'),
(11202, 11101, '2026-04-22', 'IPI', 'Industrialized Product Tax', 23560.00, NULL, 2, 'IPI 23,560.00', '2026-04-22 09:00:00'),
(11203, 11101, '2026-04-23', 'PIS', 'PIS Import', 8180.00, NULL, 3, 'PIS Import 8,180.00', '2026-04-23 09:00:00'),
(11204, 11101, '2026-04-23', 'COFINS', 'COFINS Import', 37620.00, NULL, 4, 'COFINS 37,620.00', '2026-04-23 09:00:00'),
(11205, 11101, '2026-04-25', 'ICMS', 'ICMS Sao Paulo', 42660.00, NULL, 5, 'ICMS 42,660.00', '2026-04-25 09:00:00'),
(11206, 11102, '2026-04-26', 'II', 'Import Duty', 42120.00, NULL, 1, 'II Import Duty 42,120.00', '2026-04-26 09:00:00'),
(11207, 11102, '2026-04-26', 'IPI', 'Industrialized Product Tax', 11850.00, NULL, 2, 'IPI 11,850.00', '2026-04-26 09:00:00'),
(11208, 11102, '2026-04-27', 'PIS', 'PIS Import', 5230.00, NULL, 3, 'PIS 5,230.00', '2026-04-27 09:00:00'),
(11209, 11102, '2026-04-27', 'COFINS', 'COFINS Import', 24090.00, NULL, 4, 'COFINS 24,090.00', '2026-04-27 09:00:00'),
(11210, 11102, '2026-04-28', 'ICMS', 'ICMS Parana', 18960.00, NULL, 5, 'ICMS 18,960.00', '2026-04-28 09:00:00'),
(11211, 11102, '2026-04-29', 'STORAGE', 'Terminal Storage', NULL, 3180.00, 6, 'Storage 3,180.00 debit', '2026-04-29 09:00:00'),
(11212, 11103, '2026-05-04', 'II', 'Import Duty', 39210.00, NULL, 1, 'II 39,210.00', '2026-05-04 09:00:00'),
(11213, 11103, '2026-05-04', 'IPI', 'Industrialized Product Tax', 9540.00, NULL, 2, 'IPI 9,540.00', '2026-05-04 09:00:00'),
(11214, 11103, '2026-05-05', 'PIS', 'PIS Import', 4180.00, NULL, 3, 'PIS 4,180.00', '2026-05-05 09:00:00'),
(11215, 11103, '2026-05-05', 'COFINS', 'COFINS Import', 19240.00, NULL, 4, 'COFINS 19,240.00', '2026-05-05 09:00:00'),
(11216, 11103, '2026-05-06', 'ICMS', 'ICMS Pernambuco', 19870.00, NULL, 5, 'ICMS 19,870.00', '2026-05-06 09:00:00');

INSERT INTO customs_cost_record (
    id, process_record_id, record_no, customs_fee, refund_fee, usd_amount, usd_rate,
    other_fees, total_qty, total_base, per_unit_cost, currency, note, created_by,
    created_time, updated_time
) VALUES
(11601, NULL, 'COST-LLM-NORMAL-001', 184260.0000, 0.0000, 6200.0000, 5.122000, 2800.0000, 420.0000, 218826.4000, 521.0152, 'BRL', 'LLM演示输入：正常案例，业务费用与成本记录一致', NULL, '2026-04-28 17:05:00', '2026-05-06 15:10:00'),
(11602, NULL, 'COST-LLM-RISK-002', 105430.0000, 0.0000, 3900.0000, 5.126000, 5200.0000, 2800.0000, 130621.4000, 46.6505, 'BRL', 'LLM演示输入：借贷差异、仓储费用和清关日期缺失', NULL, '2026-05-08 09:40:00', '2026-05-08 10:05:00'),
(11603, NULL, 'COST-LLM-WATCH-003', 92040.0000, 2780.0000, 2600.0000, 5.130000, 4600.0000, 160.0000, 107198.0000, 669.9875, 'BRL', 'LLM演示输入：客户余额为 FAVOR，需确认退款或抵扣', NULL, '2026-05-09 10:30:00', '2026-05-09 10:40:00');

INSERT INTO customs_cost_item (id, cost_record_id, line_no, product_name, qty, allocation_cost, unit_cost, created_time) VALUES
(11701, 11601, 1, 'CNC main spindle assembly', 120.0000, 62521.8240, 521.0152, '2026-04-28 17:05:00'),
(11702, 11601, 2, 'Servo drive unit', 180.0000, 93782.7360, 521.0152, '2026-04-28 17:05:00'),
(11703, 11601, 3, 'Precision tooling kit', 120.0000, 62521.8240, 521.0152, '2026-04-28 17:05:00'),
(11704, 11602, 1, 'Diagnostic reagent kit', 1500.0000, 69975.7500, 46.6505, '2026-05-08 09:40:00'),
(11705, 11602, 2, 'Sterile syringe pack', 1300.0000, 60645.6500, 46.6505, '2026-05-08 09:40:00'),
(11706, 11603, 1, 'Solar inverter module', 80.0000, 53599.0000, 669.9875, '2026-05-09 10:30:00'),
(11707, 11603, 2, 'MC4 connector set', 80.0000, 53599.0000, 669.9875, '2026-05-09 10:30:00');

COMMIT;
