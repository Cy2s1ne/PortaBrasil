#!/usr/bin/env python3
"""Run a functional-only PortaBrasil retest and append thesis-ready results."""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "docs" / "test-results"
BASE_SCRIPT = RESULT_DIR / "run_system_tests.py"
RUN_ID = datetime.now().strftime("%Y%m%d-%H%M%S") + "-functional-rerun"


spec = importlib.util.spec_from_file_location("system_tests", BASE_SCRIPT)
system_tests = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(system_tests)


def table(headers: list[str], rows: list[list[Any]]) -> str:
    def cell(value: Any) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    output = ["| " + " | ".join(headers) + " |"]
    output.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        output.append("| " + " | ".join(cell(item) for item in row) + " |")
    return "\n".join(output)


def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    health = system_tests.http_json("GET", "/api/health")
    login = system_tests.http_json(
        "POST",
        "/api/auth/login",
        payload={"username": "admin", "password": "admin123456"},
    )
    token = (login.get("body") or {}).get("access_token") if isinstance(login.get("body"), dict) else None
    if not token:
        raise SystemExit("登录失败，无法继续功能复测")

    suffix = datetime.now().strftime("%Y%m%d%H%M%S")
    s_ref = f"RETEST/2026/{suffix}"
    raw_text = (
        "PortaBrasil Logistica Ltda CNPJ/CPF: 41.222.333/0001-44 "
        f"Demonstrativo de Despesas No. {suffix} Cliente: Cliente Reteste Funcional "
        "Endereco Rua Reteste 200 Municipio Sao Paulo UF: SP CEP: 01310-100 CNPJ/CPF: 12.345.678/0001-90 "
        f"No. Processo: PROC-RETEST-{suffix} Export/Import: Retest Supplier Ltd S/Ref.: {s_ref} "
        "MAWB / MBL: MBL-RETEST-001 Peso Bruto: 2.000,00 DI/DUIMP/DUE: 26BRRETEST001-1 - Reg: 14/05/2026 "
        "Chegada: 13/05/2026 Destino: Santos Aviao / Navio: RETEST VESSEL Desembaraco: 14/05/2026 "
        "Carregamento: 14/05/2026 Mercadoria: Retest cargo No. NFS-e: NF-RETEST-001 "
        "FRETE: USD 1.000,00 FOB: USD 8.000,00 CIF: USD 9.000,00 No. Invoice: INV-RETEST-001 "
        "HAWB/HBL: HBL-RETEST-001 Taxa Dolar: 5,1200 Taxa Euro: 5,5300 CIF / FOB: R$ 46.080,00 "
        "14.05.2026 001 Taxa SISCOMEX 180,00 14.05.2026 002 AFRMM 320,00 "
        "14.05.2026 200 ADIANTAMENTO CLIENTE 500,00 TOTAL => 500,00 500,00 SALDO A PAGAR => 0,00"
    )

    state: dict[str, Any] = {"business_id": None, "process_id": None, "cost_record_id": None}
    functional: list[dict[str, Any]] = []

    def add(test_id: str, module: str, item: str, result: dict[str, Any]) -> None:
        functional.append(
            {
                "id": test_id,
                "module": module,
                "item": item,
                "method": result.get("method", ""),
                "path": result.get("path", ""),
                "status": result.get("status"),
                "elapsed_ms": result.get("elapsed_ms"),
                "passed": bool(result.get("passed")),
                "summary": system_tests.summarize_body(result.get("body")),
                "raw": system_tests.sanitize(result),
            }
        )

    add("F-01", "健康检查", "后端服务与数据库状态", health)
    add("F-02", "用户认证", "管理员登录", login)
    bad_login = system_tests.http_json(
        "POST",
        "/api/auth/login",
        payload={"username": "admin", "password": "wrong-password"},
    )
    bad_login["passed"] = bad_login.get("status") == 401
    add("F-03", "用户认证", "错误密码登录拦截", bad_login)
    add("F-04", "用户认证", "获取当前用户信息", system_tests.http_json("GET", "/api/auth/me", token=token))

    from_text = system_tests.http_json(
        "POST",
        "/api/documents/from-text",
        token=token,
        payload={"raw_text": raw_text, "source_page_no": 1},
        timeout=60,
    )
    if isinstance(from_text.get("body"), dict) and isinstance(from_text["body"].get("business"), dict):
        state["business_id"] = from_text["body"]["business"].get("id")
    add("F-05", "文本入库", "原始文本解析入库", from_text)

    add("F-06", "业务查询", "按 S/Ref 查询业务列表", system_tests.http_json("GET", f"/api/business?q={s_ref}", token=token))
    if state["business_id"]:
        add("F-07", "业务查询", "查询业务详情", system_tests.http_json("GET", f"/api/business/{state['business_id']}", token=token))
        add("F-08", "费用明细", "查询费用明细", system_tests.http_json("GET", f"/api/business/{state['business_id']}/fees", token=token))

    process_list = system_tests.http_json("GET", "/api/process/records?q=MBL-RETEST-001", token=token)
    if isinstance(process_list.get("body"), dict) and process_list["body"].get("items"):
        state["process_id"] = process_list["body"]["items"][0].get("id")
    add("F-09", "流程跟踪", "查询清关流程记录", process_list)
    if state["process_id"]:
        add("F-10", "流程跟踪", "查询流程详情", system_tests.http_json("GET", f"/api/process/records/{state['process_id']}", token=token))
        add(
            "F-11",
            "流程跟踪",
            "更新流程步骤状态",
            system_tests.http_json(
                "PUT",
                f"/api/process/records/{state['process_id']}/steps/10",
                token=token,
                payload={"status": "COMPLETE", "date": datetime.now().strftime("%m-%d %H:%M"), "desc": "功能复测自动更新"},
            ),
        )

    add("F-12", "仪表盘", "获取首页统计", system_tests.http_json("GET", "/api/dashboard/overview", token=token))
    add("F-13", "报表", "查询报表记录", system_tests.http_json("GET", "/api/reports/records?limit=5", token=token))
    add("F-14", "成本分析", "获取成本概览", system_tests.http_json("GET", "/api/cost/overview", token=token))
    add("F-15", "汇率接口", "获取 USD/BRL 汇率", system_tests.http_json("GET", "/api/cost/exchange-rate?base=USD&quote=BRL", token=token, timeout=20))

    cost_payload: dict[str, Any] = {
        "customs_fee": 500.0,
        "refund_fee": 0.0,
        "usd_amount": 1000.0,
        "usd_rate": 5.12,
        "other_fees": 80.0,
        "products": [{"name": "Retest Product A", "qty": 10}, {"name": "Retest Product B", "qty": 5}],
        "note": "功能复测自动生成成本记录",
    }
    if state["process_id"]:
        cost_payload["process_record_id"] = state["process_id"]
    add("F-16", "成本分析", "成本计算", system_tests.http_json("POST", "/api/cost/calculate", token=token, payload=cost_payload))
    create_cost = system_tests.http_json("POST", "/api/cost/records", token=token, payload=cost_payload)
    if isinstance(create_cost.get("body"), dict) and isinstance(create_cost["body"].get("record"), dict):
        state["cost_record_id"] = create_cost["body"]["record"].get("id")
    add("F-17", "成本分析", "保存成本记录", create_cost)
    if state["cost_record_id"]:
        add("F-18", "成本分析", "查询成本记录详情", system_tests.http_json("GET", f"/api/cost/records/{state['cost_record_id']}", token=token))

    add("F-19", "文件上传", "PDF 上传但不解析", system_tests.http_multipart_upload(ROOT / "P1.pdf", token=token, parse=False, auto_audit=False, timeout=90))
    unique_pdf = system_tests.make_unique_pdf_copy(ROOT / "P1.pdf")
    add("F-20", "外部 PDF API", "PDF 上传并调用真实解析 API 一次", system_tests.http_multipart_upload(unique_pdf, token=token, parse=True, auto_audit=False, timeout=240))

    if state["business_id"]:
        audit_payload = {"cost_record_id": state["cost_record_id"]} if state["cost_record_id"] else {}
        add(
            "F-21",
            "AI 审计",
            "AI 审计接口执行（按风险策略选择规则或 LLM）",
            system_tests.http_json("POST", f"/api/audit/business/{state['business_id']}/run", token=token, payload=audit_payload, timeout=180),
        )
    if state["cost_record_id"]:
        add(
            "F-22",
            "AI 财务复核",
            "AI 财务复核接口执行（按风险策略选择规则或 LLM）",
            system_tests.http_json("POST", f"/api/finance/cost-records/{state['cost_record_id']}/review", token=token, timeout=180),
        )

    result_path = RESULT_DIR / f"{RUN_ID}.json"
    state_path = RESULT_DIR / f"{RUN_ID}-state.json"
    result_path.write_text(json.dumps(functional, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    rows = [
        [row["id"], row["module"], row["item"], row["status"], "通过" if row["passed"] else "未通过", row["elapsed_ms"], row["summary"]]
        for row in functional
    ]
    section = f"""

## 七、功能测试复测结果

- 测试时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 测试说明：本轮重新执行功能测试；PDF 解析真实外部 API 调用 1 次，上传解析时关闭自动审计；AI 审计与财务复核按系统风险策略执行。
- 原始结果：`docs/test-results/{RUN_ID}.json`

功能复测共 {len(functional)} 项，通过 {sum(1 for row in functional if row["passed"])} 项。

{table(["编号", "模块", "测试内容", "HTTP 状态", "结果", "耗时/ms", "摘要"], rows)}
"""
    report_path = ROOT / "docs" / "系统测试报告.md"
    report_text = report_path.read_text(encoding="utf-8")
    marker = "\n## 七、功能测试复测结果\n"
    if marker in report_text:
        report_text = report_text.split(marker)[0]
    report_path.write_text(report_text + section, encoding="utf-8")

    print(json.dumps({"run_id": RUN_ID, "passed": sum(1 for row in functional if row["passed"]), "total": len(functional)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
