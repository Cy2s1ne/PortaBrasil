import json
from datetime import datetime
from typing import Any

from app.services.llm_service import LLMService


AUDIT_PROMPT = """
你是一名巴西清关业务审计专家。请只返回 JSON 对象，不要返回任何额外文本。
你需要输出业务记录中的风险、异常与改进建议。

输出 JSON 结构：
{
  "risk_level": "LOW|MEDIUM|HIGH",
  "score": 0-100,
  "summary": "一句话摘要",
  "checks": [
    {"name": "检查项", "status": "PASS|WARN|FAIL", "details": "说明"}
  ],
  "findings": [
    {
      "finding_type": "RISK|ANOMALY|SUGGESTION",
      "severity": "LOW|MEDIUM|HIGH",
      "rule_code": "规则编号或空",
      "title": "问题标题",
      "description": "问题描述",
      "evidence": "证据字段或数值",
      "suggestion": "处理建议",
      "amount": 数字或null
    }
  ]
}
"""


FINANCE_PROMPT = """
你是一名财务核算与成本控制专家。请只返回 JSON 对象，不要返回任何额外文本。
你要评估该成本记录的健康度、异常点和财务建议。

输出 JSON 结构：
{
  "health_level": "GOOD|WATCH|RISK",
  "score": 0-100,
  "summary": "一句话摘要",
  "metrics": {
    "gross_margin_hint": "可选字符串",
    "cost_pressure": "LOW|MEDIUM|HIGH",
    "fx_sensitivity": "LOW|MEDIUM|HIGH"
  },
  "items": [
    {
      "severity": "LOW|MEDIUM|HIGH",
      "title": "问题标题",
      "description": "问题描述",
      "recommendation": "建议"
    }
  ]
}
"""


def now_string() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _to_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)

    raw = str(value).strip()
    if not raw:
        return default
    raw = raw.replace("R$", "").replace("$", "").replace(" ", "")

    if raw.count(",") == 1 and raw.count(".") == 0:
        raw = raw.replace(",", ".")
    elif raw.count(",") >= 1 and raw.count(".") >= 1:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    else:
        raw = raw.replace(",", "")

    try:
        return float(raw)
    except Exception:
        return default


def _dumps_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)


def _loads_json_text(raw: Any) -> Any:
    if not raw:
        return None
    try:
        return json.loads(str(raw))
    except Exception:
        return None


def _normalize_level(value: Any, allowed: set[str], default: str) -> str:
    level = str(value or "").strip().upper()
    return level if level in allowed else default


def _normalize_score(value: Any, default: float = 70.0) -> float:
    score = _to_float(value, default)
    if score < 0:
        return 0.0
    if score > 100:
        return 100.0
    return round(score, 2)


def _highest_severity(findings: list[dict[str, Any]]) -> str:
    order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    best = "LOW"
    for item in findings:
        sev = _normalize_level(item.get("severity"), {"LOW", "MEDIUM", "HIGH"}, "LOW")
        if order[sev] > order[best]:
            best = sev
    return best


def _risk_level_from_findings(findings: list[dict[str, Any]]) -> str:
    highest = _highest_severity(findings)
    if highest == "HIGH":
        return "HIGH"
    if highest == "MEDIUM":
        return "MEDIUM"
    return "LOW"


def _health_from_items(items: list[dict[str, Any]]) -> str:
    highest = _highest_severity(items)
    if highest == "HIGH":
        return "RISK"
    if highest == "MEDIUM":
        return "WATCH"
    return "GOOD"


def _fetch_cost_record(db, cost_record_id: int) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    with db.connection() as conn:
        record = db.fetchone(
            conn,
            "SELECT * FROM customs_cost_record WHERE id = " + db.placeholder,
            [cost_record_id],
        )
        if not record:
            return None, []
        items = db.fetchall(
            conn,
            "SELECT id, line_no, product_name, qty, allocation_cost, unit_cost "
            "FROM customs_cost_item WHERE cost_record_id = "
            + db.placeholder
            + " ORDER BY line_no ASC, id ASC",
            [cost_record_id],
        )
    return record, items


def _fetch_business(db, business_id: int) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    with db.connection() as conn:
        business = db.fetchone(
            conn,
            "SELECT * FROM customs_business WHERE id = " + db.placeholder,
            [business_id],
        )
        if not business:
            return None, []
        fees = db.fetchall(
            conn,
            "SELECT id, fee_date, fee_code, fee_name, credit_amount, debit_amount, line_no "
            "FROM customs_business_fee_item WHERE business_id = "
            + db.placeholder
            + " ORDER BY line_no ASC, id ASC",
            [business_id],
        )
    return business, fees


def _build_rule_audit(business: dict[str, Any], fee_items: list[dict[str, Any]], cost_record: dict[str, Any] | None) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    total_credit = _to_float(business.get("total_credit"))
    total_debit = _to_float(business.get("total_debit"))
    balance_amount = _to_float(business.get("balance_amount"))
    fee_credit = sum(_to_float(row.get("credit_amount")) for row in fee_items)
    fee_debit = sum(_to_float(row.get("debit_amount")) for row in fee_items)

    calc_balance = total_debit - total_credit
    diff = abs(calc_balance - balance_amount)
    if (total_credit > 0 or total_debit > 0) and diff > max(1.0, abs(balance_amount) * 0.05):
        findings.append(
            {
                "finding_type": "ANOMALY",
                "severity": "HIGH",
                "rule_code": "BALANCE_MISMATCH",
                "title": "借贷与余额不一致",
                "description": "总借方-总贷方与记录余额差异较大，存在记账风险。",
                "evidence": f"calc_balance={calc_balance:.2f}, balance_amount={balance_amount:.2f}, diff={diff:.2f}",
                "suggestion": "复核原始单据与会计分录，确认币种与四舍五入规则。",
                "amount": round(diff, 2),
            }
        )
        checks.append({"name": "借贷平衡校验", "status": "FAIL", "details": "记录存在明显差异"})
    else:
        checks.append({"name": "借贷平衡校验", "status": "PASS", "details": "总账与余额基本一致"})

    fee_diff = abs((fee_debit - fee_credit) - balance_amount)
    if fee_items and fee_diff > max(1.0, abs(balance_amount) * 0.08):
        findings.append(
            {
                "finding_type": "RISK",
                "severity": "MEDIUM",
                "rule_code": "FEE_TOTAL_DIFF",
                "title": "费用明细汇总与主单不一致",
                "description": "费用明细借贷汇总与主单余额存在偏差。",
                "evidence": f"fee_net={fee_debit - fee_credit:.2f}, balance_amount={balance_amount:.2f}",
                "suggestion": "检查是否有遗漏费用行或重复行。",
                "amount": round(fee_diff, 2),
            }
        )
        checks.append({"name": "费用汇总一致性", "status": "WARN", "details": "存在偏差，建议复核"})
    else:
        checks.append({"name": "费用汇总一致性", "status": "PASS", "details": "费用与主单一致"})

    if not fee_items:
        findings.append(
            {
                "finding_type": "RISK",
                "severity": "HIGH",
                "rule_code": "NO_FEE_ITEMS",
                "title": "未解析到费用明细",
                "description": "当前业务没有费用明细，无法完成完整审计。",
                "evidence": "fee_items_count=0",
                "suggestion": "重新解析单据或人工补录费用明细。",
                "amount": None,
            }
        )

    required_fields = ["invoice_no", "nf_no", "di_duimp_due", "customer_tax_no"]
    missing_fields = [field for field in required_fields if not str(business.get(field) or "").strip()]
    if missing_fields:
        findings.append(
            {
                "finding_type": "RISK",
                "severity": "MEDIUM",
                "rule_code": "MISSING_CORE_FIELDS",
                "title": "核心字段缺失",
                "description": f"缺失字段: {', '.join(missing_fields)}",
                "evidence": ", ".join(missing_fields),
                "suggestion": "补齐票据编号、税号和申报编号后再进入财务流程。",
                "amount": None,
            }
        )

    if cost_record:
        refund_fee = _to_float(cost_record.get("refund_fee"))
        customs_fee = _to_float(cost_record.get("customs_fee"))
        if refund_fee > customs_fee and customs_fee > 0:
            findings.append(
                {
                    "finding_type": "ANOMALY",
                    "severity": "HIGH",
                    "rule_code": "REFUND_OVER_CUSTOMS",
                    "title": "退款金额超过海关总费用",
                    "description": "退款费用异常，可能存在录入错误。",
                    "evidence": f"refund_fee={refund_fee:.2f}, customs_fee={customs_fee:.2f}",
                    "suggestion": "复核退款凭证与对应税费项目。",
                    "amount": round(refund_fee - customs_fee, 2),
                }
            )

    risk_level = _risk_level_from_findings(findings)
    score = 92.0
    for finding in findings:
        sev = _normalize_level(finding.get("severity"), {"LOW", "MEDIUM", "HIGH"}, "LOW")
        if sev == "HIGH":
            score -= 20
        elif sev == "MEDIUM":
            score -= 10
        else:
            score -= 4
    score = _normalize_score(score, 75.0)
    summary = f"规则审计完成：{len(findings)} 个问题，风险等级 {risk_level}。"

    return {
        "risk_level": risk_level,
        "score": score,
        "summary": summary,
        "checks": checks,
        "findings": findings,
        "source": "RULE",
    }


def _normalize_audit_response(data: dict[str, Any]) -> dict[str, Any]:
    findings_raw = data.get("findings")
    findings: list[dict[str, Any]] = []
    if isinstance(findings_raw, list):
        for row in findings_raw:
            if not isinstance(row, dict):
                continue
            findings.append(
                {
                    "finding_type": _normalize_level(row.get("finding_type"), {"RISK", "ANOMALY", "SUGGESTION"}, "RISK"),
                    "severity": _normalize_level(row.get("severity"), {"LOW", "MEDIUM", "HIGH"}, "MEDIUM"),
                    "rule_code": str(row.get("rule_code") or "").strip() or None,
                    "title": str(row.get("title") or "").strip() or "未命名问题",
                    "description": str(row.get("description") or "").strip(),
                    "evidence": str(row.get("evidence") or "").strip() or None,
                    "suggestion": str(row.get("suggestion") or "").strip() or None,
                    "amount": round(_to_float(row.get("amount")), 4) if row.get("amount") is not None else None,
                }
            )

    checks = data.get("checks") if isinstance(data.get("checks"), list) else []
    risk_level = _normalize_level(data.get("risk_level"), {"LOW", "MEDIUM", "HIGH"}, _risk_level_from_findings(findings))
    score = _normalize_score(data.get("score"), 72.0)
    summary = str(data.get("summary") or "").strip() or f"模型审计完成：{len(findings)} 个发现。"
    return {
        "risk_level": risk_level,
        "score": score,
        "summary": summary,
        "checks": checks,
        "findings": findings,
        "source": "LLM",
    }


def _build_rule_finance(record: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []

    customs_fee = _to_float(record.get("customs_fee"))
    refund_fee = _to_float(record.get("refund_fee"))
    usd_rate = _to_float(record.get("usd_rate"))
    total_qty = _to_float(record.get("total_qty"))
    total_base = _to_float(record.get("total_base"))
    per_unit_cost = _to_float(record.get("per_unit_cost"))

    item_qty_sum = sum(_to_float(item.get("qty")) for item in items)

    if total_qty <= 0:
        issues.append(
            {
                "severity": "HIGH",
                "title": "总数量为 0",
                "description": "总数量为 0，单件成本计算缺乏有效基础。",
                "recommendation": "补录商品数量并重新核算。",
            }
        )
    if abs(item_qty_sum - total_qty) > max(1.0, total_qty * 0.02):
        issues.append(
            {
                "severity": "MEDIUM",
                "title": "明细数量与汇总数量不一致",
                "description": f"明细数量合计 {item_qty_sum:.2f} 与总数量 {total_qty:.2f} 不一致。",
                "recommendation": "检查成本明细行是否缺失或重复。",
            }
        )
    if refund_fee > customs_fee and customs_fee > 0:
        issues.append(
            {
                "severity": "HIGH",
                "title": "退款费用超过海关费用",
                "description": "退款金额异常，可能会导致总成本失真。",
                "recommendation": "核对退款凭证、币种及录入规则。",
            }
        )
    if usd_rate <= 0 or usd_rate > 20:
        issues.append(
            {
                "severity": "HIGH",
                "title": "汇率异常",
                "description": f"usd_rate={usd_rate:.6f}，超出合理区间。",
                "recommendation": "核对实时汇率来源并重新计算。",
            }
        )
    if per_unit_cost <= 0:
        issues.append(
            {
                "severity": "MEDIUM",
                "title": "单件成本异常",
                "description": "单件成本小于等于 0，不符合常见业务逻辑。",
                "recommendation": "检查费用或数量字段是否录入错误。",
            }
        )
    if total_base > 0 and len(items) == 0:
        issues.append(
            {
                "severity": "MEDIUM",
                "title": "缺少商品成本分摊明细",
                "description": "存在总成本但无明细项，难以支持审计追踪。",
                "recommendation": "补充商品维度成本明细。",
            }
        )

    score = 95.0
    for issue in issues:
        sev = _normalize_level(issue.get("severity"), {"LOW", "MEDIUM", "HIGH"}, "LOW")
        if sev == "HIGH":
            score -= 18
        elif sev == "MEDIUM":
            score -= 9
        else:
            score -= 4
    score = _normalize_score(score, 80.0)

    health_level = _health_from_items(issues)
    summary = f"规则核算分析完成：{len(issues)} 个关注点，健康度 {health_level}。"
    metrics = {
        "gross_margin_hint": "缺少销售侧数据，无法直接计算毛利率。",
        "cost_pressure": "HIGH" if per_unit_cost > 5000 else "MEDIUM" if per_unit_cost > 1000 else "LOW",
        "fx_sensitivity": "HIGH" if usd_rate > 8 else "MEDIUM" if usd_rate > 5 else "LOW",
    }

    return {
        "health_level": health_level,
        "score": score,
        "summary": summary,
        "metrics": metrics,
        "items": issues,
        "source": "RULE",
    }


def _normalize_finance_response(data: dict[str, Any]) -> dict[str, Any]:
    raw_items = data.get("items")
    items: list[dict[str, Any]] = []
    if isinstance(raw_items, list):
        for row in raw_items:
            if not isinstance(row, dict):
                continue
            items.append(
                {
                    "severity": _normalize_level(row.get("severity"), {"LOW", "MEDIUM", "HIGH"}, "MEDIUM"),
                    "title": str(row.get("title") or "").strip() or "未命名问题",
                    "description": str(row.get("description") or "").strip(),
                    "recommendation": str(row.get("recommendation") or "").strip() or None,
                }
            )

    health_level = _normalize_level(data.get("health_level"), {"GOOD", "WATCH", "RISK"}, _health_from_items(items))
    score = _normalize_score(data.get("score"), 75.0)
    summary = str(data.get("summary") or "").strip() or f"模型财务分析完成：{len(items)} 个关注点。"
    metrics = data.get("metrics") if isinstance(data.get("metrics"), dict) else {}
    return {
        "health_level": health_level,
        "score": score,
        "summary": summary,
        "metrics": metrics,
        "items": items,
        "source": "LLM",
    }


def _serialize_audit_run(row: dict[str, Any], findings: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": int(row["id"]),
        "business_id": int(row["business_id"]),
        "cost_record_id": row.get("cost_record_id"),
        "source": row.get("source"),
        "model_name": row.get("model_name"),
        "status": row.get("status"),
        "risk_level": row.get("risk_level"),
        "score": _to_float(row.get("score")),
        "summary": row.get("summary"),
        "checks": _loads_json_text(row.get("checks_json")) or [],
        "input_snapshot": _loads_json_text(row.get("input_json")) or {},
        "error_message": row.get("error_message"),
        "created_by": row.get("created_by"),
        "created_time": row.get("created_time"),
        "updated_time": row.get("updated_time"),
        "findings": findings,
    }


def _serialize_finance_review(row: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": int(row["id"]),
        "cost_record_id": int(row["cost_record_id"]),
        "source": row.get("source"),
        "model_name": row.get("model_name"),
        "status": row.get("status"),
        "health_level": row.get("health_level"),
        "score": _to_float(row.get("score")),
        "summary": row.get("summary"),
        "metrics": _loads_json_text(row.get("metrics_json")) or {},
        "input_snapshot": _loads_json_text(row.get("input_json")) or {},
        "error_message": row.get("error_message"),
        "created_by": row.get("created_by"),
        "created_time": row.get("created_time"),
        "updated_time": row.get("updated_time"),
        "items": items,
    }


def run_audit_review(
    db,
    *,
    business_id: int,
    cost_record_id: int | None = None,
    created_by: int | None = None,
) -> dict[str, Any]:
    business, fee_items = _fetch_business(db, business_id)
    if not business:
        raise LookupError("业务记录不存在")

    cost_record = None
    if cost_record_id is not None:
        cost_record, _ = _fetch_cost_record(db, cost_record_id)
        if not cost_record:
            raise LookupError("成本记录不存在")

    snapshot = {
        "business": business,
        "fee_items": fee_items,
        "cost_record": cost_record,
    }
    llm = LLMService()
    source = "LLM" if llm.enabled else "RULE"

    with db.connection() as conn:
        run_id = db.insert(
            conn,
            "ai_audit_run",
            {
                "business_id": business_id,
                "cost_record_id": cost_record_id,
                "source": source,
                "model_name": llm.model if llm.enabled else None,
                "status": "PROCESSING",
                "created_by": created_by,
                "input_json": _dumps_json(snapshot),
                "created_time": now_string(),
                "updated_time": now_string(),
            },
        )

    result_data: dict[str, Any]
    model_name = llm.model if llm.enabled else None
    raw_output = None
    error_message = None
    try:
        if llm.enabled:
            llm_payload, meta = llm.complete_json(system_prompt=AUDIT_PROMPT, user_payload=snapshot)
            normalized = _normalize_audit_response(llm_payload)
            model_name = meta.get("model") or model_name
            raw_output = _dumps_json(llm_payload)
            result_data = normalized
        else:
            result_data = _build_rule_audit(business, fee_items, cost_record)
            raw_output = _dumps_json(result_data)
    except Exception as exc:
        error_message = str(exc)
        fallback = _build_rule_audit(business, fee_items, cost_record)
        fallback["summary"] = f"{fallback['summary']}（模型调用失败，已切换规则引擎）"
        result_data = fallback
        raw_output = _dumps_json({"error": str(exc), "fallback": fallback})
        source = "RULE"

    with db.connection() as conn:
        db.update_by_id(
            conn,
            "ai_audit_run",
            run_id,
            {
                "source": result_data.get("source", source),
                "model_name": model_name,
                "status": "SUCCESS",
                "risk_level": result_data["risk_level"],
                "score": result_data["score"],
                "summary": result_data["summary"],
                "checks_json": _dumps_json(result_data.get("checks", [])),
                "raw_output": raw_output,
                "error_message": error_message,
                "updated_time": now_string(),
            },
        )

        db.execute(conn, "DELETE FROM ai_audit_finding WHERE audit_run_id = " + db.placeholder, [run_id])
        for finding in result_data.get("findings", []):
            db.insert(
                conn,
                "ai_audit_finding",
                {
                    "audit_run_id": run_id,
                    "finding_type": finding.get("finding_type"),
                    "severity": finding.get("severity"),
                    "rule_code": finding.get("rule_code"),
                    "title": finding.get("title"),
                    "description": finding.get("description"),
                    "evidence": finding.get("evidence"),
                    "suggestion": finding.get("suggestion"),
                    "amount": finding.get("amount"),
                    "created_time": now_string(),
                },
            )

        run_row = db.fetchone(conn, "SELECT * FROM ai_audit_run WHERE id = " + db.placeholder, [run_id])
        findings = db.fetchall(
            conn,
            "SELECT id, finding_type, severity, rule_code, title, description, evidence, suggestion, amount, created_time "
            "FROM ai_audit_finding WHERE audit_run_id = "
            + db.placeholder
            + " ORDER BY id ASC",
            [run_id],
        )
    return _serialize_audit_run(run_row, findings)


def run_finance_review(db, *, cost_record_id: int, created_by: int | None = None) -> dict[str, Any]:
    record, items = _fetch_cost_record(db, cost_record_id)
    if not record:
        raise LookupError("成本记录不存在")

    snapshot = {"cost_record": record, "cost_items": items}
    llm = LLMService()
    source = "LLM" if llm.enabled else "RULE"

    with db.connection() as conn:
        review_id = db.insert(
            conn,
            "ai_finance_review",
            {
                "cost_record_id": cost_record_id,
                "source": source,
                "model_name": llm.model if llm.enabled else None,
                "status": "PROCESSING",
                "created_by": created_by,
                "input_json": _dumps_json(snapshot),
                "created_time": now_string(),
                "updated_time": now_string(),
            },
        )

    result_data: dict[str, Any]
    model_name = llm.model if llm.enabled else None
    raw_output = None
    error_message = None
    try:
        if llm.enabled:
            llm_payload, meta = llm.complete_json(system_prompt=FINANCE_PROMPT, user_payload=snapshot)
            result_data = _normalize_finance_response(llm_payload)
            model_name = meta.get("model") or model_name
            raw_output = _dumps_json(llm_payload)
        else:
            result_data = _build_rule_finance(record, items)
            raw_output = _dumps_json(result_data)
    except Exception as exc:
        error_message = str(exc)
        fallback = _build_rule_finance(record, items)
        fallback["summary"] = f"{fallback['summary']}（模型调用失败，已切换规则引擎）"
        result_data = fallback
        raw_output = _dumps_json({"error": str(exc), "fallback": fallback})
        source = "RULE"

    with db.connection() as conn:
        db.update_by_id(
            conn,
            "ai_finance_review",
            review_id,
            {
                "source": result_data.get("source", source),
                "model_name": model_name,
                "status": "SUCCESS",
                "health_level": result_data["health_level"],
                "score": result_data["score"],
                "summary": result_data["summary"],
                "metrics_json": _dumps_json(result_data.get("metrics", {})),
                "raw_output": raw_output,
                "error_message": error_message,
                "updated_time": now_string(),
            },
        )
        db.execute(conn, "DELETE FROM ai_finance_item WHERE finance_review_id = " + db.placeholder, [review_id])
        for item in result_data.get("items", []):
            db.insert(
                conn,
                "ai_finance_item",
                {
                    "finance_review_id": review_id,
                    "severity": item.get("severity"),
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "recommendation": item.get("recommendation"),
                    "created_time": now_string(),
                },
            )

        review_row = db.fetchone(conn, "SELECT * FROM ai_finance_review WHERE id = " + db.placeholder, [review_id])
        review_items = db.fetchall(
            conn,
            "SELECT id, severity, title, description, recommendation, created_time "
            "FROM ai_finance_item WHERE finance_review_id = "
            + db.placeholder
            + " ORDER BY id ASC",
            [review_id],
        )
    return _serialize_finance_review(review_row, review_items)

