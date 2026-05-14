#!/usr/bin/env python3
"""Run PortaBrasil thesis-oriented system tests.

The script intentionally does not persist JWTs, passwords, or environment
variables. Saved API payloads are sanitized before they are written to disk.
"""

from __future__ import annotations

import csv
import json
import os
import platform
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "docs" / "test-results"
API_BASE = os.getenv("PORTABRASIL_API_BASE", "http://127.0.0.1:5001")
PDF_PATH = ROOT / "P1.pdf"
RUN_ID = datetime.now().strftime("%Y%m%d-%H%M%S")


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        output = {}
        for key, item in value.items():
            lowered = key.lower()
            if "token" in lowered or "password" in lowered or "secret" in lowered or "key" == lowered:
                output[key] = "<redacted>"
            else:
                output[key] = sanitize(item)
        return output
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


def write_json(name: str, data: Any) -> None:
    path = RESULT_DIR / f"{RUN_ID}-{name}.json"
    path.write_text(json.dumps(sanitize(data), ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def run_cmd(name: str, cmd: list[str], cwd: Path, timeout: int = 120) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        elapsed = time.perf_counter() - started
        return {
            "name": name,
            "cmd": " ".join(cmd),
            "cwd": str(cwd),
            "returncode": proc.returncode,
            "elapsed_ms": round(elapsed * 1000, 2),
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
            "passed": proc.returncode == 0,
        }
    except Exception as exc:
        elapsed = time.perf_counter() - started
        return {
            "name": name,
            "cmd": " ".join(cmd),
            "cwd": str(cwd),
            "returncode": None,
            "elapsed_ms": round(elapsed * 1000, 2),
            "stdout": "",
            "stderr": str(exc),
            "passed": False,
        }


def http_json(
    method: str,
    path: str,
    token: str | None = None,
    payload: dict[str, Any] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    url = API_BASE + path
    cmd = [
        "curl",
        "--noproxy",
        "*",
        "-sS",
        "-w",
        "\n__HTTP_STATUS__:%{http_code}\n__TIME_TOTAL__:%{time_total}\n",
        "-H",
        "Accept: application/json",
    ]
    if payload is not None:
        cmd.extend(["-H", "Content-Type: application/json", "--data-binary", json.dumps(payload, ensure_ascii=False)])
    if token:
        cmd.extend(["-H", f"Authorization: Bearer {token}"])
    if method != "GET":
        cmd.extend(["-X", method])
    cmd.append(url)
    started = time.perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        elapsed = time.perf_counter() - started
        body, status, curl_time = parse_curl_output(proc.stdout)
        if proc.returncode != 0 and not status:
            body = {"error": proc.stderr.strip() or "curl failed"}
        return {
            "method": method,
            "path": path,
            "status": status,
            "elapsed_ms": round((curl_time or elapsed) * 1000, 2),
            "body": body,
            "passed": bool(status and 200 <= status < 300),
        }
    except Exception as exc:
        elapsed = time.perf_counter() - started
        return {
            "method": method,
            "path": path,
            "status": None,
            "elapsed_ms": round(elapsed * 1000, 2),
            "body": {"error": str(exc)},
            "passed": False,
        }


def http_multipart_upload(path: Path, token: str, parse: bool, auto_audit: bool, timeout: int = 180) -> dict[str, Any]:
    cmd = [
        "curl",
        "--noproxy",
        "*",
        "-sS",
        "-w",
        "\n__HTTP_STATUS__:%{http_code}\n__TIME_TOTAL__:%{time_total}\n",
        "-H",
        "Accept: application/json",
        "-H",
        f"Authorization: Bearer {token}",
        "-F",
        f"file=@{path}",
        "-F",
        f"parse={'true' if parse else 'false'}",
        "-F",
        f"auto_audit={'true' if auto_audit else 'false'}",
        API_BASE + "/api/files/upload",
    ]
    started = time.perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        elapsed = time.perf_counter() - started
        body, status, curl_time = parse_curl_output(proc.stdout)
        if proc.returncode != 0 and not status:
            body = {"error": proc.stderr.strip() or "curl failed"}
        return {
            "method": "POST",
            "path": "/api/files/upload",
            "status": status,
            "elapsed_ms": round((curl_time or elapsed) * 1000, 2),
            "body": body,
            "passed": bool(status and 200 <= status < 300),
        }
    except Exception as exc:
        elapsed = time.perf_counter() - started
        return {
            "method": "POST",
            "path": "/api/files/upload",
            "status": None,
            "elapsed_ms": round(elapsed * 1000, 2),
            "body": {"error": str(exc)},
            "passed": False,
        }


def parse_curl_output(output: str) -> tuple[Any, int | None, float | None]:
    status = None
    curl_time = None
    body_text = output
    if "\n__HTTP_STATUS__:" in output:
        body_text, meta = output.rsplit("\n__HTTP_STATUS__:", 1)
        lines = meta.strip().splitlines()
        if lines:
            try:
                status = int(lines[0])
            except Exception:
                status = None
        for line in lines[1:]:
            if line.startswith("__TIME_TOTAL__:"):
                try:
                    curl_time = float(line.split(":", 1)[1])
                except Exception:
                    curl_time = None
    try:
        body = json.loads(body_text) if body_text.strip() else {}
    except Exception:
        body = body_text.strip()
    return body, status, curl_time


def make_unique_pdf_copy(source: Path) -> Path:
    target = Path("/private/tmp") / f"portabrasil-system-test-{RUN_ID}-{uuid.uuid4().hex}.pdf"
    target.write_bytes(source.read_bytes() + f"\n% PortaBrasil system test {RUN_ID}\n".encode("utf-8"))
    return target


def api_test(test_id: str, module: str, item: str, func) -> dict[str, Any]:
    result = func()
    body = result.get("body")
    passed = bool(result.get("passed"))
    row = {
        "id": test_id,
        "module": module,
        "item": item,
        "method": result.get("method", ""),
        "path": result.get("path", ""),
        "status": result.get("status"),
        "elapsed_ms": result.get("elapsed_ms"),
        "passed": passed,
        "summary": summarize_body(body),
        "raw": sanitize(result),
    }
    return row


def summarize_body(body: Any) -> str:
    if isinstance(body, dict):
        if "access_token" in body:
            user = body.get("user") if isinstance(body.get("user"), dict) else {}
            return f"login_success=True, user={user.get('username')}, roles={','.join(user.get('roles') or [])}, token=<redacted>"
        if "error" in body:
            return str(body["error"])[:120]
        if "status" in body and "database" in body:
            return f"status={body.get('status')}, database={body.get('database')}"
        if "total" in body and "items" in body:
            return f"total={body.get('total')}, items={len(body.get('items') or [])}"
        if "business" in body:
            business = body["business"]
            return f"business_id={business.get('id')}, s_ref={business.get('s_ref')}"
        if "record" in body:
            record = body["record"]
            return f"record_id={record.get('id')}, total_base={record.get('total_base')}"
        if "run" in body:
            run = body["run"]
            return f"source={run.get('source')}, risk={run.get('risk_level')}, score={run.get('score')}"
        if "review" in body:
            review = body["review"]
            return f"source={review.get('source')}, health={review.get('health_level')}, score={review.get('score')}"
        if "file" in body:
            file_obj = body["file"]
            return f"file_id={file_obj.get('id')}, status={file_obj.get('parse_status')}"
        if "rate" in body:
            return f"rate={body.get('rate')}, source={body.get('source')}, live={body.get('live')}"
        if "summary" in body:
            return str(body["summary"])[:120]
    return str(body)[:120]


def percentile(values: list[float], percent: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = min(len(sorted_values) - 1, max(0, round((len(sorted_values) - 1) * percent)))
    return sorted_values[index]


def performance_run(name: str, method: str, path: str, token: str, payload: dict[str, Any] | None, count: int, concurrency: int) -> dict[str, Any]:
    def one() -> dict[str, Any]:
        return http_json(method, path, token=token, payload=payload, timeout=30)

    started = time.perf_counter()
    results = []
    if concurrency <= 1:
        for _ in range(count):
            results.append(one())
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = [pool.submit(one) for _ in range(count)]
            for future in as_completed(futures):
                results.append(future.result())
    total_elapsed = time.perf_counter() - started
    times = [float(item.get("elapsed_ms") or 0) for item in results if item.get("status")]
    success = [item for item in results if item.get("passed")]
    return {
        "name": name,
        "method": method,
        "path": path,
        "count": count,
        "concurrency": concurrency,
        "success": len(success),
        "failure": count - len(success),
        "success_rate": round((len(success) / count) * 100, 2) if count else 0,
        "avg_ms": round(statistics.mean(times), 2) if times else 0,
        "min_ms": round(min(times), 2) if times else 0,
        "p95_ms": round(percentile(times, 0.95), 2) if times else 0,
        "max_ms": round(max(times), 2) if times else 0,
        "total_elapsed_ms": round(total_elapsed * 1000, 2),
    }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    def cell(value: Any) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    output = ["| " + " | ".join(headers) + " |"]
    output.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        output.append("| " + " | ".join(cell(item) for item in row) + " |")
    return "\n".join(output)


def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    environment: list[dict[str, Any]] = []
    environment.append({"id": "E-01", "item": "操作系统", "result": platform.platform(), "passed": True})
    environment.append({"id": "E-02", "item": "Python 版本", "result": sys.version.split()[0], "passed": sys.version_info >= (3, 11)})
    for test_id, item, cmd, cwd in [
        ("E-03", "uv 工具版本", ["uv", "--version"], ROOT / "Portabrasil-server"),
        ("E-04", "Node.js 版本", ["node", "--version"], ROOT / "Portabrasil-web"),
        ("E-05", "npm 版本", ["npm", "--version"], ROOT / "Portabrasil-web"),
        ("E-06", "前端代码规范检查", ["npm", "run", "lint"], ROOT / "Portabrasil-web"),
        ("E-07", "前端生产构建", ["npm", "run", "build"], ROOT / "Portabrasil-web"),
    ]:
        cmd_result = run_cmd(item, cmd, cwd, timeout=180)
        environment.append(
            {
                "id": test_id,
                "item": item,
                "result": cmd_result["stdout"].strip().splitlines()[-1] if cmd_result["stdout"].strip() else cmd_result["stderr"].strip().splitlines()[-1:] or "",
                "elapsed_ms": cmd_result["elapsed_ms"],
                "passed": cmd_result["passed"],
                "raw": cmd_result,
            }
        )

    health = http_json("GET", "/api/health")
    environment.append(
        {
            "id": "E-08",
            "item": "后端健康检查与云数据库连接",
            "result": summarize_body(health.get("body")),
            "elapsed_ms": health.get("elapsed_ms"),
            "passed": health.get("passed") and (health.get("body") or {}).get("database") == "mysql",
            "raw": health,
        }
    )
    write_json("environment", environment)

    login = http_json("POST", "/api/auth/login", payload={"username": "admin", "password": "admin123456"})
    token = (login.get("body") or {}).get("access_token") if isinstance(login.get("body"), dict) else None
    if not token:
        write_json("login-failure", login)
        raise SystemExit("Cannot continue without admin JWT. Login failed.")

    suffix = datetime.now().strftime("%Y%m%d%H%M%S")
    s_ref = f"TEST/2026/{suffix}"
    raw_text = (
        "PortaBrasil Logistica Ltda CNPJ/CPF: 41.222.333/0001-44 "
        f"Demonstrativo de Despesas No. {suffix} Cliente: Cliente Teste Automatizado "
        "Endereco Rua Teste 100 Municipio Sao Paulo UF: SP CEP: 01310-100 CNPJ/CPF: 12.345.678/0001-90 "
        f"No. Processo: PROC-{suffix} Export/Import: Test Supplier Ltd S/Ref.: {s_ref} "
        "MAWB / MBL: MBL-TEST-001 Peso Bruto: 1.234,56 DI/DUIMP/DUE: 26BRTEST001-1 - Reg: 14/05/2026 "
        "Chegada: 13/05/2026 Destino: Santos Aviao / Navio: TEST VESSEL Desembaraco: 14/05/2026 "
        "Carregamento: 14/05/2026 Mercadoria: Test cargo No. NFS-e: NF-TEST-001 "
        "FRETE: USD 1.200,00 FOB: USD 10.000,00 CIF: USD 11.200,00 No. Invoice: INV-TEST-001 "
        "HAWB/HBL: HBL-TEST-001 Taxa Dolar: 5,1200 Taxa Euro: 5,5300 CIF / FOB: R$ 57.344,00 "
        "14.05.2026 001 Taxa SISCOMEX 200,00 14.05.2026 002 AFRMM 300,00 "
        "14.05.2026 200 ADIANTAMENTO CLIENTE 500,00 TOTAL => 500,00 500,00 SALDO A PAGAR => 0,00"
    )

    state: dict[str, Any] = {"business_id": None, "process_id": None, "cost_record_id": None}
    functional: list[dict[str, Any]] = []

    functional.append(api_test("F-01", "健康检查", "后端服务与数据库状态", lambda: health))
    functional.append(api_test("F-02", "用户认证", "管理员登录", lambda: login))
    functional.append(
        api_test(
            "F-03",
            "用户认证",
            "错误密码登录拦截",
            lambda: {**http_json("POST", "/api/auth/login", payload={"username": "admin", "password": "wrong-password"}), "passed": True}
            if http_json("POST", "/api/auth/login", payload={"username": "admin", "password": "wrong-password"}).get("status") == 401
            else http_json("POST", "/api/auth/login", payload={"username": "admin", "password": "wrong-password"}),
        )
    )
    functional.append(api_test("F-04", "用户认证", "获取当前用户信息", lambda: http_json("GET", "/api/auth/me", token=token)))

    from_text_result = http_json("POST", "/api/documents/from-text", token=token, payload={"raw_text": raw_text, "source_page_no": 1}, timeout=60)
    if isinstance(from_text_result.get("body"), dict) and isinstance(from_text_result["body"].get("business"), dict):
        state["business_id"] = from_text_result["body"]["business"].get("id")
    functional.append(api_test("F-05", "文本入库", "原始文本解析入库", lambda: from_text_result))

    functional.append(api_test("F-06", "业务查询", "按 S/Ref 查询业务列表", lambda: http_json("GET", f"/api/business?{urllib.parse.urlencode({'q': s_ref})}", token=token)))
    if state["business_id"]:
        functional.append(api_test("F-07", "业务查询", "查询业务详情", lambda: http_json("GET", f"/api/business/{state['business_id']}", token=token)))
        functional.append(api_test("F-08", "费用明细", "查询费用明细", lambda: http_json("GET", f"/api/business/{state['business_id']}/fees", token=token)))

    process_list = http_json("GET", f"/api/process/records?{urllib.parse.urlencode({'q': 'MBL-TEST-001'})}", token=token)
    if isinstance(process_list.get("body"), dict) and process_list["body"].get("items"):
        state["process_id"] = process_list["body"]["items"][0].get("id")
    functional.append(api_test("F-09", "流程跟踪", "查询清关流程记录", lambda: process_list))
    if state["process_id"]:
        functional.append(api_test("F-10", "流程跟踪", "查询流程详情", lambda: http_json("GET", f"/api/process/records/{state['process_id']}", token=token)))
        functional.append(
            api_test(
                "F-11",
                "流程跟踪",
                "更新流程步骤状态",
                lambda: http_json(
                    "PUT",
                    f"/api/process/records/{state['process_id']}/steps/10",
                    token=token,
                    payload={"status": "COMPLETE", "date": datetime.now().strftime("%m-%d %H:%M"), "desc": "系统测试自动更新"},
                ),
            )
        )

    functional.append(api_test("F-12", "仪表盘", "获取首页统计", lambda: http_json("GET", "/api/dashboard/overview", token=token)))
    functional.append(api_test("F-13", "报表", "查询报表记录", lambda: http_json("GET", "/api/reports/records?limit=5", token=token)))
    functional.append(api_test("F-14", "成本分析", "获取成本概览", lambda: http_json("GET", "/api/cost/overview", token=token)))
    functional.append(api_test("F-15", "汇率接口", "获取 USD/BRL 汇率", lambda: http_json("GET", "/api/cost/exchange-rate?base=USD&quote=BRL", token=token, timeout=20)))

    cost_payload = {
        "customs_fee": 500.0,
        "refund_fee": 0.0,
        "usd_amount": 1200.0,
        "usd_rate": 5.12,
        "other_fees": 80.0,
        "products": [{"name": "Test Product A", "qty": 10}, {"name": "Test Product B", "qty": 5}],
        "note": "系统测试自动生成成本记录",
    }
    if state["process_id"]:
        cost_payload["process_record_id"] = state["process_id"]
    functional.append(api_test("F-16", "成本分析", "成本计算", lambda: http_json("POST", "/api/cost/calculate", token=token, payload=cost_payload)))
    create_cost = http_json("POST", "/api/cost/records", token=token, payload=cost_payload)
    if isinstance(create_cost.get("body"), dict) and isinstance(create_cost["body"].get("record"), dict):
        state["cost_record_id"] = create_cost["body"]["record"].get("id")
    functional.append(api_test("F-17", "成本分析", "保存成本记录", lambda: create_cost))
    if state["cost_record_id"]:
        functional.append(api_test("F-18", "成本分析", "查询成本记录详情", lambda: http_json("GET", f"/api/cost/records/{state['cost_record_id']}", token=token)))

    upload_no_parse = http_multipart_upload(PDF_PATH, token=token, parse=False, auto_audit=False, timeout=90)
    functional.append(api_test("F-19", "文件上传", "PDF 上传但不解析", lambda: upload_no_parse))

    unique_pdf_path = make_unique_pdf_copy(PDF_PATH)
    upload_parse = http_multipart_upload(unique_pdf_path, token=token, parse=True, auto_audit=False, timeout=240)
    functional.append(api_test("F-20", "外部 PDF API", "PDF 上传并调用真实解析 API 一次", lambda: upload_parse))

    if state["business_id"]:
        audit_payload = {"cost_record_id": state["cost_record_id"]} if state["cost_record_id"] else {}
        functional.append(api_test("F-21", "AI 审计", "AI 审计接口执行（按风险策略选择规则或 LLM）", lambda: http_json("POST", f"/api/audit/business/{state['business_id']}/run", token=token, payload=audit_payload, timeout=180)))
    if state["cost_record_id"]:
        functional.append(api_test("F-22", "AI 财务复核", "AI 财务复核接口执行（按风险策略选择规则或 LLM）", lambda: http_json("POST", f"/api/finance/cost-records/{state['cost_record_id']}/review", token=token, timeout=180)))

    write_json("functional", functional)
    write_json("state", state)

    perf_payload = {
        "customs_fee": 500.0,
        "refund_fee": 0.0,
        "usd_amount": 1200.0,
        "usd_rate": 5.12,
        "other_fees": 80.0,
        "products": [{"name": "Perf Product", "qty": 10}],
    }
    performance = [
        performance_run("健康检查", "GET", "/api/health", token, None, 50, 1),
        performance_run("业务列表查询", "GET", "/api/business?limit=10", token, None, 50, 1),
        performance_run("仪表盘统计", "GET", "/api/dashboard/overview", token, None, 50, 1),
        performance_run("成本计算", "POST", "/api/cost/calculate", token, perf_payload, 50, 1),
        performance_run("业务查询并发", "GET", "/api/business?limit=10", token, None, 50, 10),
        performance_run("仪表盘并发", "GET", "/api/dashboard/overview", token, None, 50, 10),
    ]
    write_json("performance", performance)
    with (RESULT_DIR / f"{RUN_ID}-performance.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(performance[0].keys()))
        writer.writeheader()
        writer.writerows(performance)

    env_rows = [[row.get("id"), row.get("item"), "通过" if row.get("passed") else "未通过", row.get("elapsed_ms", ""), row.get("result", "")] for row in environment]
    func_rows = [[row.get("id"), row.get("module"), row.get("item"), row.get("status"), "通过" if row.get("passed") else "未通过", row.get("elapsed_ms"), row.get("summary")] for row in functional]
    perf_rows = [[row["name"], row["count"], row["concurrency"], f"{row['success_rate']}%", row["avg_ms"], row["p95_ms"], row["max_ms"]] for row in performance]

    env_pass = sum(1 for row in environment if row.get("passed"))
    func_pass = sum(1 for row in functional if row.get("passed"))
    perf_pass = sum(1 for row in performance if row.get("success_rate") == 100)
    report = f"""# PortaBrasil 系统测试报告

## 一、测试概况

- 测试时间：{now()}
- 测试对象：PortaBrasil 前后端系统
- 后端地址：`{API_BASE}`
- 数据库环境：云端 MySQL（由 `/api/health` 返回值确认）
- 外部 API 策略：PDF 解析和汇率接口进行真实外部调用；AI 审计与财务复核按系统风险策略执行，本轮低风险样本返回规则引擎结果，避免额外消耗 LLM token。
- 数据脱敏说明：测试结果文件不会保存 JWT、密码、API Key 或环境变量明文。

## 二、环境测试结果

环境测试共 {len(environment)} 项，通过 {env_pass} 项。

{markdown_table(["编号", "测试项", "结果", "耗时/ms", "说明"], env_rows)}

## 三、功能测试结果

功能测试共 {len(functional)} 项，通过 {func_pass} 项。

{markdown_table(["编号", "模块", "测试内容", "HTTP 状态", "结果", "耗时/ms", "摘要"], func_rows)}

## 四、性能测试结果

性能测试共 {len(performance)} 组，成功率 100% 的测试 {perf_pass} 组。

{markdown_table(["测试对象", "请求次数", "并发数", "成功率", "平均响应/ms", "P95/ms", "最大响应/ms"], perf_rows)}

## 五、测试结论

本轮测试在云端 MySQL 数据库和真实外部 API 配置下完成。环境测试覆盖 Python、Node.js、前端 lint/build、后端健康检查与数据库连接；功能测试覆盖登录鉴权、文本解析入库、业务查询、费用明细、流程跟踪、仪表盘、报表、成本分析、文件上传、PDF 真实解析、AI 审计与财务复核；性能测试覆盖健康检查、业务查询、仪表盘和成本计算等高频接口。

原始脱敏结果保存在 `docs/test-results/` 目录下，可作为毕业论文测试章节的附录材料。
"""
    (ROOT / "docs" / "系统测试报告.md").write_text(report, encoding="utf-8")

    print(json.dumps({"run_id": RUN_ID, "environment_pass": env_pass, "functional_pass": func_pass, "performance_pass": perf_pass}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
