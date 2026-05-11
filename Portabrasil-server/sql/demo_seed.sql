-- PortaBrasil demo data insert script.
-- Execute this file after the database schema has been created.
--
-- Recommended:
--   1. Run sql/demo_seed_delete.sql first if you imported this demo data before.
--   2. Run this file to insert demo data.

BEGIN;

INSERT INTO pdf_file (id, file_name, file_path, file_size, file_hash, page_count, parse_status, upload_time, remark) VALUES
(9001, 'demo_invoice_santos_001.pdf', 'uploads/demo/demo_invoice_santos_001.pdf', 638420, 'demo_hash_santos_001', 5, 'SUCCESS', '2026-04-21 10:15:00', '演示数据：Santos进口清关单据'),
(9002, 'demo_invoice_itajai_002.pdf', 'uploads/demo/demo_invoice_itajai_002.pdf', 712884, 'demo_hash_itajai_002', 4, 'SUCCESS', '2026-04-25 14:22:00', '演示数据：Itajai进口清关单据'),
(9003, 'demo_export_paranagua_003.pdf', 'uploads/demo/demo_export_paranagua_003.pdf', 522910, 'demo_hash_paranagua_003', 3, 'SUCCESS', '2026-04-28 11:06:00', '演示数据：Paranagua出口单据');

INSERT INTO pdf_parse_task (id, file_id, task_no, parser_type, status, start_time, end_time, error_message, raw_result, created_time, updated_time) VALUES
(9001, 9001, 'TASK-DEMO-20260421-001', 'LLM', 'SUCCESS', '2026-04-21 10:15:12', '2026-04-21 10:16:08', NULL, '{"s_ref":"S/2026-IMP-001","status":"parsed"}', '2026-04-21 10:15:12', '2026-04-21 10:16:08'),
(9002, 9002, 'TASK-DEMO-20260425-002', 'LLM', 'SUCCESS', '2026-04-25 14:22:10', '2026-04-25 14:23:02', NULL, '{"s_ref":"S/2026-IMP-002","status":"parsed"}', '2026-04-25 14:22:10', '2026-04-25 14:23:02'),
(9003, 9003, 'TASK-DEMO-20260428-003', 'LLM', 'SUCCESS', '2026-04-28 11:06:19', '2026-04-28 11:06:54', NULL, '{"s_ref":"S/2026-EXP-003","status":"parsed"}', '2026-04-28 11:06:19', '2026-04-28 11:06:54');

INSERT INTO customs_business (
    id, s_ref, n_ref, document_no, invoice_no, nf_no, process_no, business_type,
    trade_company, customer_name, customer_address, customer_city, customer_state,
    customer_zip_code, customer_tax_no, issuer_name, issuer_tax_no, mawb_mbl,
    hawb_hbl, di_duimp_due, registration_date, arrival_date, customs_clearance_date,
    loading_date, destination, vessel_flight_name, gross_weight, volume_count,
    cargo_desc, freight_currency, freight_amount, fob_currency, fob_amount,
    cif_currency, cif_amount, cif_brl_amount, dollar_rate, euro_rate,
    total_credit, total_debit, balance_amount, balance_direction,
    source_file_id, source_page_no, data_status, created_time, updated_time
) VALUES
(9101, 'S/2026-IMP-001', 'N/BR-2026-00418', 'DEM-2026-0418', 'INV-CN-20418', 'NF-904188', 'PROC-SSZ-260418', 'IMPORT', 'Shenzhen Nova Machinery Co., Ltd.', 'Alfa Auto Pecas Ltda.', 'Av. Paulista 1100', 'Sao Paulo', 'SP', '01310-100', '12.345.678/0001-90', 'PortaBrasil Logistica Ltda.', '41.222.333/0001-44', 'MAWB-7845120091', 'HBL-SZX-260418-A', '26BR00041891-7', '2026-04-18', '2026-04-21', '2026-04-27', '2026-04-28', 'Campinas Distribution Center', 'MSC ARIANE', 12840.500, 42, 'CNC machining centers and spare parts', 'USD', 6200.00, 'USD', 84200.00, 'USD', 90400.00, 463028.80, 5.122000, 5.530000, 184260.00, 184260.00, 0.00, 'BALANCED', 9001, 2, 'CONFIRMED', '2026-04-21 10:16:30', '2026-05-06 15:12:00'),
(9102, 'S/2026-IMP-002', 'N/BR-2026-00452', 'DEM-2026-0452', 'INV-HK-20452', 'NF-904529', 'PROC-ITJ-260452', 'IMPORT', 'Guangzhou MedSupply Export Ltd.', 'BioSaude Equipamentos Medicos SA', 'Rua XV de Novembro 245', 'Curitiba', 'PR', '80020-310', '28.774.119/0001-65', 'PortaBrasil Logistica Ltda.', '41.222.333/0001-44', 'MBL-ITJ-88924512', 'HBL-CAN-260452-B', '26BR00045232-1', '2026-04-22', '2026-04-25', NULL, NULL, 'Curitiba Warehouse', 'EVER LEADER', 6840.000, 28, 'Sterile medical consumables and diagnostic kits', 'USD', 3900.00, 'USD', 51600.00, 'USD', 55500.00, 284493.00, 5.126000, 5.541000, 103850.00, 105430.00, 1580.00, 'PAYABLE', 9002, 1, 'REVIEWING', '2026-04-25 14:24:00', '2026-05-08 09:35:00'),
(9103, 'S/2026-EXP-003', 'N/BR-2026-00470', 'DEM-2026-0470', 'EXP-BR-20470', 'NF-EXP-0470', 'PROC-PNG-260470', 'EXPORT', 'Cafe Serra Alta Exportadora Ltda.', 'Lusitania Foods Importacao Lda.', 'Rua do Comercio 88', 'Lisbon', 'LX', '1100-150', 'PT-509772118', 'PortaBrasil Logistica Ltda.', '41.222.333/0001-44', 'MBL-PNG-55210490', 'HBL-PNG-260470-C', '26BRDUE047000-3', '2026-04-27', '2026-04-28', '2026-05-02', '2026-05-04', 'Port of Lisbon', 'MAERSK LIMA', 22000.000, 310, 'Roasted coffee beans', 'USD', 4800.00, 'USD', 73500.00, 'USD', 78300.00, 401615.60, 5.129000, 5.548000, 76840.00, 76840.00, 0.00, 'BALANCED', 9003, 1, 'CONFIRMED', '2026-04-28 11:07:20', '2026-05-05 13:41:00'),
(9104, 'S/2026-IMP-004', 'N/BR-2026-00491', 'DEM-2026-0491', 'INV-KR-20491', 'NF-904911', 'PROC-GIG-260491', 'IMPORT', 'Busan Smart Components Inc.', 'Energia Solar Nordeste Ltda.', NULL, 'Recife', 'PE', NULL, '33.908.221/0001-02', 'PortaBrasil Logistica Ltda.', '41.222.333/0001-44', 'AWB-988220412', 'HAWB-ICN-260491-D', '26BR00049187-0', '2026-04-30', '2026-05-03', NULL, NULL, 'Recife Solar Plant', 'KE Cargo 273', 3420.750, 16, 'Photovoltaic inverters and connectors', 'USD', 2600.00, 'USD', 41750.00, 'USD', 44350.00, 227496.80, 5.130000, NULL, 94820.00, 92040.00, 2780.00, 'FAVOR', NULL, NULL, 'REVIEWING', '2026-05-03 08:45:00', '2026-05-09 10:22:00'),
(9105, 'S/2026-IMP-005', 'N/BR-2026-00508', 'DEM-2026-0508', 'INV-US-20508', 'NF-905081', 'PROC-VCP-260508', 'IMPORT', 'Austin Lab Instruments LLC', 'Laboratorio Atlantico SA', NULL, 'Sao Paulo', 'SP', NULL, '77.512.019/0001-73', 'PortaBrasil Logistica Ltda.', '41.222.333/0001-44', 'AWB-045988721', 'HAWB-DFW-260508-E', '26BR00050811-5', '2026-05-04', '2026-05-05', '2026-05-09', NULL, 'Sao Paulo Lab Hub', 'AA Cargo 963', 920.300, 9, 'Laboratory spectrometers', 'USD', 1850.00, 'USD', 36800.00, 'USD', 38650.00, 198351.80, 5.132000, NULL, 64510.00, 64510.00, 0.00, 'BALANCED', NULL, NULL, 'CONFIRMED', '2026-05-05 11:50:00', '2026-05-09 14:10:00');

INSERT INTO customs_business_fee_item (id, business_id, fee_date, fee_code, fee_name, credit_amount, debit_amount, line_no, raw_text, created_time) VALUES
(9201, 9101, '2026-04-22', 'II', 'Import Duty', 72240.00, NULL, 1, 'II Import Duty 72,240.00', '2026-04-22 09:00:00'),
(9202, 9101, '2026-04-22', 'IPI', 'Industrialized Product Tax', 23560.00, NULL, 2, 'IPI 23,560.00', '2026-04-22 09:00:00'),
(9203, 9101, '2026-04-23', 'PIS', 'PIS Import', 8180.00, NULL, 3, 'PIS Import 8,180.00', '2026-04-23 09:00:00'),
(9204, 9101, '2026-04-23', 'COFINS', 'COFINS Import', 37620.00, NULL, 4, 'COFINS 37,620.00', '2026-04-23 09:00:00'),
(9205, 9101, '2026-04-25', 'ICMS', 'ICMS Sao Paulo', 42660.00, NULL, 5, 'ICMS 42,660.00', '2026-04-25 09:00:00'),
(9206, 9102, '2026-04-26', 'II', 'Import Duty', 42120.00, NULL, 1, 'II Import Duty 42,120.00', '2026-04-26 09:00:00'),
(9207, 9102, '2026-04-26', 'IPI', 'Industrialized Product Tax', 11850.00, NULL, 2, 'IPI 11,850.00', '2026-04-26 09:00:00'),
(9208, 9102, '2026-04-27', 'PIS', 'PIS Import', 5230.00, NULL, 3, 'PIS 5,230.00', '2026-04-27 09:00:00'),
(9209, 9102, '2026-04-27', 'COFINS', 'COFINS Import', 24090.00, NULL, 4, 'COFINS 24,090.00', '2026-04-27 09:00:00'),
(9210, 9102, '2026-04-28', 'ICMS', 'ICMS Parana', 18960.00, NULL, 5, 'ICMS 18,960.00', '2026-04-28 09:00:00'),
(9211, 9102, '2026-04-29', 'STORAGE', 'Terminal Storage', NULL, 3180.00, 6, 'Storage 3,180.00 debit', '2026-04-29 09:00:00'),
(9212, 9103, '2026-04-29', 'DOC', 'Export Documentation Fee', 12840.00, NULL, 1, 'Export doc fee 12,840.00', '2026-04-29 09:00:00'),
(9213, 9103, '2026-04-29', 'THC', 'Terminal Handling Charge', 28800.00, NULL, 2, 'THC 28,800.00', '2026-04-29 09:00:00'),
(9214, 9103, '2026-05-01', 'FREIGHT', 'Ocean Freight Recharge', 35200.00, NULL, 3, 'Freight recharge 35,200.00', '2026-05-01 09:00:00'),
(9215, 9104, '2026-05-04', 'II', 'Import Duty', 39210.00, NULL, 1, 'II 39,210.00', '2026-05-04 09:00:00'),
(9216, 9104, '2026-05-04', 'IPI', 'Industrialized Product Tax', 9540.00, NULL, 2, 'IPI 9,540.00', '2026-05-04 09:00:00'),
(9217, 9104, '2026-05-05', 'PIS', 'PIS Import', 4180.00, NULL, 3, 'PIS 4,180.00', '2026-05-05 09:00:00'),
(9218, 9104, '2026-05-05', 'COFINS', 'COFINS Import', 19240.00, NULL, 4, 'COFINS 19,240.00', '2026-05-05 09:00:00'),
(9219, 9104, '2026-05-06', 'ICMS', 'ICMS Pernambuco', 19870.00, NULL, 5, 'ICMS 19,870.00', '2026-05-06 09:00:00'),
(9220, 9105, '2026-05-05', 'II', 'Import Duty', 22040.00, NULL, 1, 'II 22,040.00', '2026-05-05 09:00:00'),
(9221, 9105, '2026-05-06', 'IPI', 'Industrialized Product Tax', 8120.00, NULL, 2, 'IPI 8,120.00', '2026-05-06 09:00:00'),
(9222, 9105, '2026-05-06', 'PIS', 'PIS Import', 3660.00, NULL, 3, 'PIS 3,660.00', '2026-05-06 09:00:00'),
(9223, 9105, '2026-05-07', 'COFINS', 'COFINS Import', 16840.00, NULL, 4, 'COFINS 16,840.00', '2026-05-07 09:00:00'),
(9224, 9105, '2026-05-07', 'ICMS', 'ICMS Sao Paulo', 13850.00, NULL, 5, 'ICMS 13,850.00', '2026-05-07 09:00:00');

INSERT INTO customs_process_record (id, business_id, bl_no, goods_desc, declaration_date, port_name, overall_status, created_time, updated_time) VALUES
(9301, 9101, 'BL-DEMO-SSZ-001', 'CNC machining centers and spare parts', '2026-04-22', 'Santos (SSZ)', 'CLEARED', '2026-04-21 10:30:00', '2026-04-28 16:45:00'),
(9302, 9102, 'BL-DEMO-ITJ-002', 'Sterile medical consumables and diagnostic kits', '2026-04-26', 'Itajai (ITJ)', 'INSPECTION', '2026-04-25 14:40:00', '2026-05-08 09:50:00'),
(9303, 9103, 'BL-DEMO-PNG-003', 'Roasted coffee beans', '2026-04-29', 'Paranagua (PNG)', 'CLEARED', '2026-04-28 11:20:00', '2026-05-04 18:05:00'),
(9304, 9104, 'BL-DEMO-GIG-004', 'Photovoltaic inverters and connectors', '2026-05-04', 'Rio de Janeiro (GIG)', 'PROCESSING', '2026-05-03 09:00:00', '2026-05-09 10:45:00'),
(9305, 9105, 'BL-DEMO-VCP-005', 'Laboratory spectrometers', '2026-05-05', 'Viracopos (VCP)', 'CLEARED', '2026-05-05 12:10:00', '2026-05-09 14:20:00');

INSERT INTO customs_process_step (id, process_id, step_no, status, completion_time, step_desc, created_time, updated_time) VALUES
(9401, 9301, 1, 'COMPLETE', '04-22 09:00', '单据接收', '2026-04-22 09:00:00', '2026-04-22 09:00:00'),
(9402, 9301, 2, 'COMPLETE', '04-22 14:00', '商业发票校验', '2026-04-22 14:00:00', '2026-04-22 14:00:00'),
(9403, 9301, 3, 'COMPLETE', '04-23 10:30', '装箱单校验', '2026-04-23 10:30:00', '2026-04-23 10:30:00'),
(9404, 9301, 4, 'COMPLETE', '04-24 11:20', '税费预估', '2026-04-24 11:20:00', '2026-04-24 11:20:00'),
(9405, 9301, 5, 'COMPLETE', '04-25 15:40', '申报提交', '2026-04-25 15:40:00', '2026-04-25 15:40:00'),
(9406, 9301, 6, 'COMPLETE', '04-26 10:10', '海关通道判定', '2026-04-26 10:10:00', '2026-04-26 10:10:00'),
(9407, 9301, 7, 'COMPLETE', '04-27 16:25', '税费支付', '2026-04-27 16:25:00', '2026-04-27 16:25:00'),
(9408, 9301, 8, 'COMPLETE', '04-28 09:35', '海关放行', '2026-04-28 09:35:00', '2026-04-28 09:35:00'),
(9409, 9301, 9, 'COMPLETE', '04-28 13:50', '提货安排', '2026-04-28 13:50:00', '2026-04-28 13:50:00'),
(9410, 9301, 10, 'COMPLETE', '04-28 17:10', '归档完成', '2026-04-28 17:10:00', '2026-04-28 17:10:00'),
(9411, 9302, 1, 'COMPLETE', '04-26 09:00', '单据接收', '2026-04-26 09:00:00', '2026-04-26 09:00:00'),
(9412, 9302, 2, 'COMPLETE', '04-26 14:00', '商业发票校验', '2026-04-26 14:00:00', '2026-04-26 14:00:00'),
(9413, 9302, 3, 'COMPLETE', '04-27 10:30', '装箱单校验', '2026-04-27 10:30:00', '2026-04-27 10:30:00'),
(9414, 9302, 4, 'COMPLETE', '04-28 11:20', '税费预估', '2026-04-28 11:20:00', '2026-04-28 11:20:00'),
(9415, 9302, 5, 'COMPLETE', '04-29 15:40', '申报提交', '2026-04-29 15:40:00', '2026-04-29 15:40:00'),
(9416, 9302, 6, 'COMPLETE', '05-02 10:10', '海关通道判定', '2026-05-02 10:10:00', '2026-05-02 10:10:00'),
(9417, 9302, 7, 'PENDING', NULL, '税费支付', '2026-05-02 10:10:00', '2026-05-02 10:10:00'),
(9418, 9302, 8, 'PENDING', NULL, '海关放行', '2026-05-02 10:10:00', '2026-05-02 10:10:00'),
(9419, 9302, 9, 'PENDING', NULL, '提货安排', '2026-05-02 10:10:00', '2026-05-02 10:10:00'),
(9420, 9302, 10, 'PENDING', NULL, '归档完成', '2026-05-02 10:10:00', '2026-05-02 10:10:00'),
(9421, 9303, 1, 'COMPLETE', '04-29 09:00', '单据接收', '2026-04-29 09:00:00', '2026-04-29 09:00:00'),
(9422, 9303, 2, 'COMPLETE', '04-29 14:00', '商业发票校验', '2026-04-29 14:00:00', '2026-04-29 14:00:00'),
(9423, 9303, 3, 'COMPLETE', '04-30 10:30', '装箱单校验', '2026-04-30 10:30:00', '2026-04-30 10:30:00'),
(9424, 9303, 4, 'COMPLETE', '05-01 11:20', '税费预估', '2026-05-01 11:20:00', '2026-05-01 11:20:00'),
(9425, 9303, 5, 'COMPLETE', '05-01 15:40', '申报提交', '2026-05-01 15:40:00', '2026-05-01 15:40:00'),
(9426, 9303, 6, 'COMPLETE', '05-02 10:10', '海关通道判定', '2026-05-02 10:10:00', '2026-05-02 10:10:00'),
(9427, 9303, 7, 'COMPLETE', '05-03 16:25', '税费支付', '2026-05-03 16:25:00', '2026-05-03 16:25:00'),
(9428, 9303, 8, 'COMPLETE', '05-04 09:35', '海关放行', '2026-05-04 09:35:00', '2026-05-04 09:35:00'),
(9429, 9303, 9, 'COMPLETE', '05-04 13:50', '提货安排', '2026-05-04 13:50:00', '2026-05-04 13:50:00'),
(9430, 9303, 10, 'COMPLETE', '05-04 17:10', '归档完成', '2026-05-04 17:10:00', '2026-05-04 17:10:00'),
(9431, 9304, 1, 'COMPLETE', '05-04 09:00', '单据接收', '2026-05-04 09:00:00', '2026-05-04 09:00:00'),
(9432, 9304, 2, 'COMPLETE', '05-04 14:00', '商业发票校验', '2026-05-04 14:00:00', '2026-05-04 14:00:00'),
(9433, 9304, 3, 'COMPLETE', '05-05 10:30', '装箱单校验', '2026-05-05 10:30:00', '2026-05-05 10:30:00'),
(9434, 9304, 4, 'COMPLETE', '05-06 11:20', '税费预估', '2026-05-06 11:20:00', '2026-05-06 11:20:00'),
(9435, 9304, 5, 'PENDING', NULL, '申报提交', '2026-05-06 11:20:00', '2026-05-06 11:20:00'),
(9436, 9304, 6, 'PENDING', NULL, '海关通道判定', '2026-05-06 11:20:00', '2026-05-06 11:20:00'),
(9437, 9304, 7, 'PENDING', NULL, '税费支付', '2026-05-06 11:20:00', '2026-05-06 11:20:00'),
(9438, 9304, 8, 'PENDING', NULL, '海关放行', '2026-05-06 11:20:00', '2026-05-06 11:20:00'),
(9439, 9304, 9, 'PENDING', NULL, '提货安排', '2026-05-06 11:20:00', '2026-05-06 11:20:00'),
(9440, 9304, 10, 'PENDING', NULL, '归档完成', '2026-05-06 11:20:00', '2026-05-06 11:20:00'),
(9441, 9305, 1, 'COMPLETE', '05-05 09:00', '单据接收', '2026-05-05 09:00:00', '2026-05-05 09:00:00'),
(9442, 9305, 2, 'COMPLETE', '05-05 14:00', '商业发票校验', '2026-05-05 14:00:00', '2026-05-05 14:00:00'),
(9443, 9305, 3, 'COMPLETE', '05-06 10:30', '装箱单校验', '2026-05-06 10:30:00', '2026-05-06 10:30:00'),
(9444, 9305, 4, 'COMPLETE', '05-07 11:20', '税费预估', '2026-05-07 11:20:00', '2026-05-07 11:20:00'),
(9445, 9305, 5, 'COMPLETE', '05-07 15:40', '申报提交', '2026-05-07 15:40:00', '2026-05-07 15:40:00'),
(9446, 9305, 6, 'COMPLETE', '05-08 10:10', '海关通道判定', '2026-05-08 10:10:00', '2026-05-08 10:10:00'),
(9447, 9305, 7, 'COMPLETE', '05-08 16:25', '税费支付', '2026-05-08 16:25:00', '2026-05-08 16:25:00'),
(9448, 9305, 8, 'COMPLETE', '05-09 09:35', '海关放行', '2026-05-09 09:35:00', '2026-05-09 09:35:00'),
(9449, 9305, 9, 'COMPLETE', '05-09 13:50', '提货安排', '2026-05-09 13:50:00', '2026-05-09 13:50:00'),
(9450, 9305, 10, 'COMPLETE', '05-09 17:10', '归档完成', '2026-05-09 17:10:00', '2026-05-09 17:10:00');

INSERT INTO customs_activity (id, activity_type, title, description, related_process_id, occurred_at) VALUES
(9501, 'SUCCESS', '审计完成：S/2026-IMP-001', '规则审计未发现金额异常，可作为正常案例展示。', 9301, '2026-05-06 15:15:00'),
(9502, 'ALERT', '审计预警：S/2026-IMP-002', '费用合计与业务借贷总额存在差异，建议财务复核。', 9302, '2026-05-08 09:58:00'),
(9503, 'INFO', '流程推进：S/2026-IMP-004', '新能源设备仍在申报处理中，等待税费支付确认。', 9304, '2026-05-09 10:50:00');

INSERT INTO customs_cost_record (
    id, process_record_id, record_no, customs_fee, refund_fee, usd_amount, usd_rate,
    other_fees, total_qty, total_base, per_unit_cost, currency, note, created_by,
    created_time, updated_time
) VALUES
(9601, 9301, 'COST-DEMO-20260428-001', 184260.0000, 0.0000, 6200.0000, 5.122000, 2800.0000, 420.0000, 218826.4000, 521.0152, 'BRL', '演示：正常审计案例，业务费用与成本记录一致', NULL, '2026-04-28 17:05:00', '2026-05-06 15:10:00'),
(9602, 9302, 'COST-DEMO-20260508-002', 105430.0000, 0.0000, 3900.0000, 5.126000, 5200.0000, 2800.0000, 130621.4000, 46.6505, 'BRL', '演示：查验与费用差异案例，适合展示审计发现项', NULL, '2026-05-08 09:40:00', '2026-05-08 10:05:00'),
(9603, 9304, 'COST-DEMO-20260509-004', 92040.0000, 2780.0000, 2600.0000, 5.130000, 4600.0000, 160.0000, 107198.0000, 669.9875, 'BRL', '演示：客户应收余额为 FAVOR，需确认是否退款或抵扣', NULL, '2026-05-09 10:30:00', '2026-05-09 10:40:00');

INSERT INTO customs_cost_item (id, cost_record_id, line_no, product_name, qty, allocation_cost, unit_cost, created_time) VALUES
(9701, 9601, 1, 'CNC main spindle assembly', 120.0000, 62521.8240, 521.0152, '2026-04-28 17:05:00'),
(9702, 9601, 2, 'Servo drive unit', 180.0000, 93782.7360, 521.0152, '2026-04-28 17:05:00'),
(9703, 9601, 3, 'Precision tooling kit', 120.0000, 62521.8240, 521.0152, '2026-04-28 17:05:00'),
(9704, 9602, 1, 'Diagnostic reagent kit', 1500.0000, 69975.7500, 46.6505, '2026-05-08 09:40:00'),
(9705, 9602, 2, 'Sterile syringe pack', 1300.0000, 60645.6500, 46.6505, '2026-05-08 09:40:00'),
(9706, 9603, 1, 'Solar inverter module', 80.0000, 53599.0000, 669.9875, '2026-05-09 10:30:00'),
(9707, 9603, 2, 'MC4 connector set', 80.0000, 53599.0000, 669.9875, '2026-05-09 10:30:00');

INSERT INTO ai_audit_run (
    id, business_id, cost_record_id, source, model_name, status, risk_level, score,
    summary, checks_json, input_json, raw_output, error_message, created_by,
    created_time, updated_time
) VALUES
(9801, 9101, 9601, 'RULE', NULL, 'SUCCESS', 'LOW', 94.00, '规则审计完成：业务借贷平衡，费用明细合计与成本记录一致，未发现重大风险。', '[{"code":"BALANCE_CHECK","name":"借贷平衡","status":"PASS"},{"code":"FEE_TOTAL_CHECK","name":"费用合计一致性","status":"PASS"},{"code":"COST_TRACE_CHECK","name":"成本记录追踪","status":"PASS"}]', '{"business_ref":"S/2026-IMP-001","cost_record_no":"COST-DEMO-20260428-001"}', '{"risk_level":"LOW","score":94,"findings":[]}', NULL, NULL, '2026-05-06 15:12:00', '2026-05-06 15:12:08'),
(9802, 9102, 9602, 'RULE', NULL, 'SUCCESS', 'HIGH', 62.00, '规则审计完成：发现借贷差异、查验状态下仓储费用偏高、成本记录缺少退款说明。', '[{"code":"BALANCE_CHECK","name":"借贷平衡","status":"WARN"},{"code":"FEE_TOTAL_CHECK","name":"费用合计一致性","status":"FAIL"},{"code":"INSPECTION_STORAGE_CHECK","name":"查验仓储费用","status":"WARN"}]', '{"business_ref":"S/2026-IMP-002","cost_record_no":"COST-DEMO-20260508-002"}', '{"risk_level":"HIGH","score":62,"finding_count":3}', NULL, NULL, '2026-05-08 09:55:00', '2026-05-08 09:55:12'),
(9803, 9104, 9603, 'RULE', NULL, 'SUCCESS', 'MEDIUM', 76.00, '规则审计完成：客户余额方向为 FAVOR，建议确认退款、抵扣或后续账期处理。', '[{"code":"BALANCE_DIRECTION_CHECK","name":"余额方向","status":"WARN"},{"code":"REFUND_TRACE_CHECK","name":"退款追踪","status":"WARN"},{"code":"FIELD_COMPLETENESS_CHECK","name":"关键字段完整性","status":"PASS"}]', '{"business_ref":"S/2026-IMP-004","cost_record_no":"COST-DEMO-20260509-004"}', '{"risk_level":"MEDIUM","score":76,"finding_count":2}', NULL, NULL, '2026-05-09 10:42:00', '2026-05-09 10:42:11');

INSERT INTO ai_audit_finding (id, audit_run_id, finding_type, severity, rule_code, title, description, evidence, suggestion, amount, created_time) VALUES
(9901, 9802, 'RISK', 'HIGH', 'BALANCE_MISMATCH', '借贷余额不一致', '业务主表显示借方高于贷方，余额方向为 PAYABLE，需要确认是否仍有未入账费用或付款差额。', 'total_credit=103850.00, total_debit=105430.00, balance_amount=1580.00', '请核对付款凭证、终端收费单与客户应付通知，确认 1,580.00 BRL 差额来源。', 1580.0000, '2026-05-08 09:55:13'),
(9902, 9802, 'RISK', 'MEDIUM', 'FEE_SUM_MISMATCH', '费用明细与业务总额存在差异', '费用明细贷方合计为 102,250.00 BRL，业务贷方为 103,850.00 BRL，存在 1,600.00 BRL 未解释差异。', 'fee_credit_sum=102250.00, business_total_credit=103850.00', '补充缺失费用行或调整业务总额后重新执行审计。', 1600.0000, '2026-05-08 09:55:13'),
(9903, 9802, 'WARNING', 'MEDIUM', 'INSPECTION_STORAGE', '查验状态下仓储费用偏高', '该流程处于 INSPECTION，且存在 3,180.00 BRL 仓储借方费用，可能影响客户结算。', 'overall_status=INSPECTION, storage_debit=3180.00', '向报关员确认查验时长和终端账单，必要时在成本备注中说明。', 3180.0000, '2026-05-08 09:55:13'),
(9904, 9803, 'WARNING', 'MEDIUM', 'BALANCE_FAVOR', '客户余额为 FAVOR', '业务记录显示客户方向为 FAVOR，可能需要退款、抵扣或转入后续账期。', 'balance_direction=FAVOR, balance_amount=2780.00', '和财务确认 2,780.00 BRL 的处理方式，并在回款记录中留痕。', 2780.0000, '2026-05-09 10:42:12'),
(9905, 9803, 'RISK', 'LOW', 'CLEARANCE_PENDING', '清关日期尚未填写', '业务仍处于 REVIEWING，清关日期为空，后续统计报表可能无法准确计算清关周期。', 'customs_clearance_date=NULL, data_status=REVIEWING', '放行后及时补录清关日期，并重新生成流程报表。', NULL, '2026-05-09 10:42:12');

INSERT INTO ai_finance_review (
    id, cost_record_id, source, model_name, status, health_level, score, summary,
    metrics_json, input_json, raw_output, error_message, created_by, created_time, updated_time
) VALUES
(10001, 9601, 'RULE', NULL, 'SUCCESS', 'HEALTHY', 91.00, '财务复核完成：单位成本稳定，成本构成清晰，可直接用于报价复盘。', '{"total_base":218826.40,"per_unit_cost":521.0152,"refund_ratio":0,"other_fee_ratio":0.0128}', '{"cost_record_no":"COST-DEMO-20260428-001"}', '{"health_level":"HEALTHY","score":91}', NULL, NULL, '2026-05-06 15:13:00', '2026-05-06 15:13:07'),
(10002, 9602, 'RULE', NULL, 'SUCCESS', 'WATCH', 68.00, '财务复核完成：查验导致仓储及其他费用占比偏高，建议单独向客户说明。', '{"total_base":130621.40,"per_unit_cost":46.6505,"other_fee_ratio":0.0398,"inspection_related_fee":3180}', '{"cost_record_no":"COST-DEMO-20260508-002"}', '{"health_level":"WATCH","score":68}', NULL, NULL, '2026-05-08 10:02:00', '2026-05-08 10:02:06');

INSERT INTO ai_finance_item (id, finance_review_id, severity, title, description, recommendation, created_time) VALUES
(10101, 10002, 'MEDIUM', '其他费用占比偏高', '其他费用 5,200.00 BRL 占总成本约 3.98%，高于常规演示阈值。', '在客户账单备注中拆分查验、仓储和终端服务费。', '2026-05-08 10:02:07'),
(10102, 10002, 'HIGH', '查验相关费用需补充凭证', '流程状态为 INSPECTION，成本记录中出现较高附加费用。', '上传终端仓储账单或在成本备注中写明凭证编号。', '2026-05-08 10:02:07');

INSERT INTO statement_summary (
    id, statement_no, issue_date, due_date, total_amount, amount_direction, customer_name,
    customer_address, customer_city, customer_state, customer_zip_code, customer_tax_no,
    issuer_name, source_file_id, source_page_no, created_time, updated_time
) VALUES
(10201, 'DEMO-0526-AUDIT', '2026-05-09', '2026-05-30', 352228.40, 'S/Favor', 'Demo Audit Customer Group', 'Av. Brasil 2600', 'Sao Paulo', 'SP', '01430-001', '00.111.222/0001-88', 'PortaBrasil Logistica Ltda.', NULL, NULL, '2026-05-09 16:00:00', '2026-05-09 16:00:00');

INSERT INTO statement_summary_item (id, summary_id, n_ref, s_ref, nf_no, amount_direction, balance_amount, business_id, line_no, created_time) VALUES
(10211, 10201, 'N/BR-2026-00418', 'S/2026-IMP-001', 'NF-904188', 'BALANCED', 0.00, 9101, 1, '2026-05-09 16:00:00'),
(10212, 10201, 'N/BR-2026-00452', 'S/2026-IMP-002', 'NF-904529', 'PAYABLE', 1580.00, 9102, 2, '2026-05-09 16:00:00'),
(10213, 10201, 'N/BR-2026-00491', 'S/2026-IMP-004', 'NF-904911', 'FAVOR', 2780.00, 9104, 3, '2026-05-09 16:00:00');

COMMIT;
