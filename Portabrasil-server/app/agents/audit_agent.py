from typing import Any, TypedDict

from app.agents.llm_factory import complete_json_with_langchain, is_langchain_llm_enabled
from app.services.audit_finance_service import (
    AUDIT_PROMPT,
    FINANCE_PROMPT,
    _build_rule_audit,
    _build_rule_finance,
    _normalize_audit_response,
    _normalize_finance_response,
)


class AuditAgentState(TypedDict, total=False):
    snapshot: dict[str, Any]
    business: dict[str, Any]
    fee_items: list[dict[str, Any]]
    cost_record: dict[str, Any] | None
    audit_plan: dict[str, Any]
    rule_result: dict[str, Any]
    model_result: dict[str, Any]
    model_payload: dict[str, Any]
    result: dict[str, Any]
    model_meta: dict[str, Any]
    trace: list[dict[str, Any]]


class FinanceAgentState(TypedDict, total=False):
    snapshot: dict[str, Any]
    record: dict[str, Any]
    items: list[dict[str, Any]]
    finance_plan: dict[str, Any]
    rule_result: dict[str, Any]
    model_result: dict[str, Any]
    model_payload: dict[str, Any]
    result: dict[str, Any]
    model_meta: dict[str, Any]
    trace: list[dict[str, Any]]


def _append_trace(state: dict[str, Any], agent: str, action: str, detail: dict[str, Any] | None = None) -> None:
    state.setdefault("trace", []).append({"agent": agent, "action": action, "detail": detail or {}})


def _to_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(str(value).replace(",", "").strip())
    except Exception:
        return default


def _audit_planner_agent(state: AuditAgentState) -> AuditAgentState:
    business = state["business"]
    fee_items = state.get("fee_items") or []
    cost_record = state.get("cost_record")
    reasons: list[str] = []
    tools = ["rule_audit"]

    required_fields = ["invoice_no", "nf_no", "di_duimp_due", "customer_tax_no"]
    missing_fields = [field for field in required_fields if not str(business.get(field) or "").strip()]
    if missing_fields:
        reasons.append("missing_core_fields")
        tools.append("data_completeness_review")
    if not fee_items:
        reasons.append("fee_items_missing")
        tools.append("data_completeness_review")

    total_credit = _to_float(business.get("total_credit"))
    total_debit = _to_float(business.get("total_debit"))
    balance_amount = _to_float(business.get("balance_amount"))
    balance_diff = abs((total_debit - total_credit) - balance_amount)
    if balance_diff > max(1.0, abs(balance_amount) * 0.05):
        reasons.append("amount_variance_detected")
        tools.append("risk_reasoning")

    if cost_record:
        refund_fee = _to_float(cost_record.get("refund_fee"))
        customs_fee = _to_float(cost_record.get("customs_fee"))
        if customs_fee > 0 and refund_fee > customs_fee:
            reasons.append("refund_over_customs_fee")
            tools.append("risk_reasoning")
        tools.append("cost_cross_check")

    llm_available = is_langchain_llm_enabled()
    should_call_llm = llm_available and ("risk_reasoning" in tools or "data_completeness_review" in tools)
    if should_call_llm and "risk_reasoning" not in tools:
        tools.append("risk_reasoning")

    plan = {
        "tools": list(dict.fromkeys(tools)),
        "reasons": reasons or ["low_risk_rule_summary"],
        "missing_fields": missing_fields,
        "balance_diff": round(balance_diff, 4),
        "llm_available": llm_available,
        "should_call_llm": should_call_llm,
    }
    state["audit_plan"] = plan
    _append_trace(state, "AuditPlannerAgent", "create_audit_plan", plan)
    return state


def _rule_audit_agent(state: AuditAgentState) -> AuditAgentState:
    result = _build_rule_audit(state["business"], state["fee_items"], state.get("cost_record"))
    state["rule_result"] = result
    _append_trace(
        state,
        "RuleAuditAgent",
        "run_deterministic_rules",
        {"risk_level": result.get("risk_level"), "findings_count": len(result.get("findings") or [])},
    )
    return state


def _risk_reasoning_agent(state: AuditAgentState) -> AuditAgentState:
    plan = state.get("audit_plan") or {}
    if not plan.get("should_call_llm"):
        _append_trace(state, "RiskReasoningAgent", "skip_llm", {"reason": "audit_plan_did_not_select_risk_reasoning", "plan": plan})
        return state

    if not is_langchain_llm_enabled():
        _append_trace(state, "RiskReasoningAgent", "skip_llm", {"reason": "api_key_or_base_url_missing"})
        return state

    payload, meta = complete_json_with_langchain(system_prompt=AUDIT_PROMPT, user_payload=state["snapshot"])
    normalized = _normalize_audit_response(payload)
    normalized["source"] = "LANGCHAIN_AGENT"
    state["model_payload"] = payload
    state["model_result"] = normalized
    state["model_meta"] = meta
    _append_trace(
        state,
        "RiskReasoningAgent",
        "langchain_structured_audit",
        {"provider": meta.get("provider"), "model": meta.get("model"), "findings_count": len(normalized.get("findings") or [])},
    )
    return state


def _audit_supervisor_agent(state: AuditAgentState) -> AuditAgentState:
    if state.get("model_result"):
        result = dict(state["model_result"])
        rule_checks = state.get("rule_result", {}).get("checks") or []
        model_checks = result.get("checks") or []
        result["checks"] = rule_checks + model_checks
        result["summary"] = f"{result['summary']}（LangChain 多智能体审计，已合并规则校验）"
        result["source"] = "LANGCHAIN_AGENT"
    else:
        result = dict(state["rule_result"])
        result["source"] = "RULE"

    state["result"] = result
    _append_trace(
        state,
        "AuditSupervisorAgent",
        "merge_agent_outputs",
        {"source": result.get("source"), "score": result.get("score"), "risk_level": result.get("risk_level"), "plan": state.get("audit_plan")},
    )
    return state


def _finance_planner_agent(state: FinanceAgentState) -> FinanceAgentState:
    record = state["record"]
    items = state.get("items") or []
    reasons: list[str] = []
    tools = ["finance_rule_check"]

    customs_fee = _to_float(record.get("customs_fee"))
    refund_fee = _to_float(record.get("refund_fee"))
    usd_rate = _to_float(record.get("usd_rate"))
    total_qty = _to_float(record.get("total_qty"))
    per_unit_cost = _to_float(record.get("per_unit_cost"))
    item_qty_sum = sum(_to_float(item.get("qty")) for item in items)

    if total_qty <= 0 or per_unit_cost <= 0:
        reasons.append("invalid_quantity_or_unit_cost")
    if total_qty > 0 and abs(item_qty_sum - total_qty) > max(1.0, total_qty * 0.02):
        reasons.append("item_quantity_mismatch")
    if customs_fee > 0 and refund_fee > customs_fee:
        reasons.append("refund_over_customs_fee")
    if usd_rate <= 0 or usd_rate > 20:
        reasons.append("fx_rate_out_of_range")
    if not items:
        reasons.append("cost_items_missing")

    if reasons:
        tools.append("finance_reasoning")

    llm_available = is_langchain_llm_enabled()
    plan = {
        "tools": list(dict.fromkeys(tools)),
        "reasons": reasons or ["low_risk_rule_summary"],
        "llm_available": llm_available,
        "should_call_llm": llm_available and bool(reasons),
        "item_qty_sum": round(item_qty_sum, 4),
    }
    state["finance_plan"] = plan
    _append_trace(state, "FinancePlannerAgent", "create_finance_plan", plan)
    return state


def _rule_finance_agent(state: FinanceAgentState) -> FinanceAgentState:
    result = _build_rule_finance(state["record"], state["items"])
    state["rule_result"] = result
    _append_trace(
        state,
        "FinanceRuleAgent",
        "run_deterministic_rules",
        {"health_level": result.get("health_level"), "items_count": len(result.get("items") or [])},
    )
    return state


def _finance_reasoning_agent(state: FinanceAgentState) -> FinanceAgentState:
    plan = state.get("finance_plan") or {}
    if not plan.get("should_call_llm"):
        _append_trace(state, "FinanceAnalystAgent", "skip_llm", {"reason": "finance_plan_did_not_select_reasoning", "plan": plan})
        return state

    if not is_langchain_llm_enabled():
        _append_trace(state, "FinanceAnalystAgent", "skip_llm", {"reason": "api_key_or_base_url_missing"})
        return state

    payload, meta = complete_json_with_langchain(system_prompt=FINANCE_PROMPT, user_payload=state["snapshot"])
    normalized = _normalize_finance_response(payload)
    normalized["source"] = "LANGCHAIN_AGENT"
    state["model_payload"] = payload
    state["model_result"] = normalized
    state["model_meta"] = meta
    _append_trace(
        state,
        "FinanceAnalystAgent",
        "langchain_structured_finance_review",
        {"provider": meta.get("provider"), "model": meta.get("model"), "items_count": len(normalized.get("items") or [])},
    )
    return state


def _finance_supervisor_agent(state: FinanceAgentState) -> FinanceAgentState:
    if state.get("model_result"):
        result = dict(state["model_result"])
        rule_items = state.get("rule_result", {}).get("items") or []
        model_items = result.get("items") or []
        result["items"] = rule_items + model_items
        result["summary"] = f"{result['summary']}（LangChain 多智能体财务复核，已合并规则校验）"
        result["source"] = "LANGCHAIN_AGENT"
    else:
        result = dict(state["rule_result"])
        result["source"] = "RULE"

    state["result"] = result
    _append_trace(
        state,
        "FinanceSupervisorAgent",
        "merge_agent_outputs",
        {"source": result.get("source"), "score": result.get("score"), "health_level": result.get("health_level"), "plan": state.get("finance_plan")},
    )
    return state


def _route_audit_after_rules(state: AuditAgentState) -> str:
    plan = state.get("audit_plan") or {}
    return "risk_reasoning_agent" if plan.get("should_call_llm") else "audit_supervisor_agent"


def _route_finance_after_rules(state: FinanceAgentState) -> str:
    plan = state.get("finance_plan") or {}
    return "finance_reasoning_agent" if plan.get("should_call_llm") else "finance_supervisor_agent"


def _compile_graph(state_type, nodes: list[tuple[str, Any]]):
    try:
        from langgraph.graph import END, StateGraph
    except Exception as exc:
        raise RuntimeError("langgraph 未安装，无法运行多智能体审计流程") from exc

    graph = StateGraph(state_type)
    for name, handler in nodes:
        graph.add_node(name, handler)
    graph.set_entry_point(nodes[0][0])
    for index in range(len(nodes) - 1):
        graph.add_edge(nodes[index][0], nodes[index + 1][0])
    graph.add_edge(nodes[-1][0], END)
    return graph.compile()


def run_business_audit_agent(
    *,
    snapshot: dict[str, Any],
    business: dict[str, Any],
    fee_items: list[dict[str, Any]],
    cost_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        from langgraph.graph import END, StateGraph
    except Exception as exc:
        raise RuntimeError("langgraph 未安装，无法运行多智能体审计流程") from exc

    graph = StateGraph(AuditAgentState)
    graph.add_node("audit_planner_agent", _audit_planner_agent)
    graph.add_node("rule_audit_agent", _rule_audit_agent)
    graph.add_node("risk_reasoning_agent", _risk_reasoning_agent)
    graph.add_node("audit_supervisor_agent", _audit_supervisor_agent)
    graph.set_entry_point("audit_planner_agent")
    graph.add_edge("audit_planner_agent", "rule_audit_agent")
    graph.add_conditional_edges(
        "rule_audit_agent",
        _route_audit_after_rules,
        {
            "risk_reasoning_agent": "risk_reasoning_agent",
            "audit_supervisor_agent": "audit_supervisor_agent",
        },
    )
    graph.add_edge("risk_reasoning_agent", "audit_supervisor_agent")
    graph.add_edge("audit_supervisor_agent", END)
    app = graph.compile()
    final_state = app.invoke(
        {
            "snapshot": snapshot,
            "business": business,
            "fee_items": fee_items,
            "cost_record": cost_record,
            "trace": [{"agent": "BusinessAuditSupervisor", "action": "start", "detail": {"business_id": business.get("id")}}],
        }
    )
    return {
        "result": final_state["result"],
        "raw_output": {
            "framework": "langchain_langgraph",
            "agent_trace": final_state.get("trace", []),
            "audit_plan": final_state.get("audit_plan"),
            "rule_result": final_state.get("rule_result"),
            "model_result": final_state.get("model_result"),
            "model_payload": final_state.get("model_payload"),
        },
        "meta": final_state.get("model_meta") or {},
    }


def run_finance_review_agent(
    *,
    snapshot: dict[str, Any],
    record: dict[str, Any],
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    try:
        from langgraph.graph import END, StateGraph
    except Exception as exc:
        raise RuntimeError("langgraph 未安装，无法运行多智能体财务复核流程") from exc

    graph = StateGraph(FinanceAgentState)
    graph.add_node("finance_planner_agent", _finance_planner_agent)
    graph.add_node("rule_finance_agent", _rule_finance_agent)
    graph.add_node("finance_reasoning_agent", _finance_reasoning_agent)
    graph.add_node("finance_supervisor_agent", _finance_supervisor_agent)
    graph.set_entry_point("finance_planner_agent")
    graph.add_edge("finance_planner_agent", "rule_finance_agent")
    graph.add_conditional_edges(
        "rule_finance_agent",
        _route_finance_after_rules,
        {
            "finance_reasoning_agent": "finance_reasoning_agent",
            "finance_supervisor_agent": "finance_supervisor_agent",
        },
    )
    graph.add_edge("finance_reasoning_agent", "finance_supervisor_agent")
    graph.add_edge("finance_supervisor_agent", END)
    app = graph.compile()
    final_state = app.invoke(
        {
            "snapshot": snapshot,
            "record": record,
            "items": items,
            "trace": [{"agent": "FinanceReviewSupervisor", "action": "start", "detail": {"cost_record_id": record.get("id")}}],
        }
    )
    return {
        "result": final_state["result"],
        "raw_output": {
            "framework": "langchain_langgraph",
            "agent_trace": final_state.get("trace", []),
            "finance_plan": final_state.get("finance_plan"),
            "rule_result": final_state.get("rule_result"),
            "model_result": final_state.get("model_result"),
            "model_payload": final_state.get("model_payload"),
        },
        "meta": final_state.get("model_meta") or {},
    }
