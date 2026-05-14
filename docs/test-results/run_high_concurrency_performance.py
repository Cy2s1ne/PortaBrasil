#!/usr/bin/env python3
"""Run the high-concurrency performance supplement for PortaBrasil."""

from __future__ import annotations

import csv
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "docs" / "test-results"
BASE_SCRIPT = RESULT_DIR / "run_system_tests.py"
RUN_ID = datetime.now().strftime("%Y%m%d-%H%M%S") + "-high-concurrency"


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
    login = system_tests.http_json(
        "POST",
        "/api/auth/login",
        payload={"username": "admin", "password": "admin123456"},
        timeout=30,
    )
    token = (login.get("body") or {}).get("access_token") if isinstance(login.get("body"), dict) else None
    if not token:
        raise SystemExit("登录失败，无法执行高并发性能测试")

    payload = {
        "customs_fee": 500.0,
        "refund_fee": 0.0,
        "usd_amount": 1200.0,
        "usd_rate": 5.12,
        "other_fees": 80.0,
        "products": [{"name": "Perf Product", "qty": 10}],
    }
    performance = [
        system_tests.performance_run("健康检查", "GET", "/api/health", token, None, 50, 10),
        system_tests.performance_run("业务列表查询", "GET", "/api/business?limit=10", token, None, 50, 100),
        system_tests.performance_run("仪表盘统计", "GET", "/api/dashboard/overview", token, None, 50, 100),
        system_tests.performance_run("成本计算", "POST", "/api/cost/calculate", token, payload, 50, 100),
        system_tests.performance_run("业务查询并发", "GET", "/api/business?limit=10", token, None, 50, 100),
        system_tests.performance_run("仪表盘并发", "GET", "/api/dashboard/overview", token, None, 50, 100),
    ]

    json_path = RESULT_DIR / f"{RUN_ID}-performance.json"
    csv_path = RESULT_DIR / f"{RUN_ID}-performance.csv"
    json_path.write_text(json.dumps(performance, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(performance[0].keys()))
        writer.writeheader()
        writer.writerows(performance)

    rows = [
        [row["name"], row["count"], row["concurrency"], f"{row['success_rate']}%", row["avg_ms"], row["p95_ms"], row["max_ms"]]
        for row in performance
    ]
    section = f"""

## 六、高并发性能补充测试

- 测试时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 测试说明：本轮只执行普通接口性能测试，不调用 PDF 解析、汇率或 AI 外部服务。
- 原始结果：`docs/test-results/{RUN_ID}-performance.json`，CSV：`docs/test-results/{RUN_ID}-performance.csv`。

{table(["测试对象", "请求次数", "并发数", "成功率", "平均响应/ms", "P95/ms", "最大响应/ms"], rows)}
"""
    report_path = ROOT / "docs" / "系统测试报告.md"
    report = report_path.read_text(encoding="utf-8")
    marker = "\n## 六、高并发性能补充测试\n"
    if marker in report:
        report = report.split(marker)[0]
    report_path.write_text(report + section, encoding="utf-8")

    print(json.dumps({"run_id": RUN_ID, "performance": performance}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
