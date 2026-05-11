import os
from typing import Any, TypedDict

from parser_rules import parse_demonstrativo_text
from pdf_parser import PDFParser


class PDFIngestionState(TypedDict, total=False):
    db: Any
    pdf_file: dict[str, Any]
    task: dict[str, Any]
    created_by: int | None
    auto_audit: bool
    parser_plan: dict[str, Any]
    parse_attempts: list[dict[str, Any]]
    current_tool_type: str
    current_file_type: str
    parse_error: str
    quality: dict[str, Any]
    parser_result: dict[str, Any]
    content: str
    business: dict[str, Any]
    audit: dict[str, Any]
    audit_error: str
    validation: dict[str, Any]
    trace: list[dict[str, Any]]


def _append_trace(state: PDFIngestionState, agent: str, action: str, detail: dict[str, Any] | None = None) -> None:
    state.setdefault("trace", []).append({"agent": agent, "action": action, "detail": detail or {}})


def _parser_strategy_agent(state: PDFIngestionState) -> PDFIngestionState:
    pdf_file = state["pdf_file"]
    file_size = int(pdf_file.get("file_size") or 0)
    preferred_tool = (os.getenv("ZHIPU_PDF_TOOL_TYPE") or "lite").strip()
    tool_candidates = [preferred_tool]
    if preferred_tool != "prime":
        tool_candidates.append("prime")

    plan = {
        "file_type": (os.getenv("ZHIPU_PDF_FILE_TYPE") or "PDF").strip(),
        "tool_candidates": tool_candidates,
        "current_index": 0,
        "min_content_length": 300 if file_size > 80 * 1024 else 120,
        "required_fields": ["s_ref"],
        "reason": "start_with_fast_lite_then_escalate_to_prime_when_quality_is_low",
    }
    state["parser_plan"] = plan
    state["current_tool_type"] = tool_candidates[0]
    state["current_file_type"] = plan["file_type"]
    state["parse_attempts"] = []
    _append_trace(
        state,
        "ParserStrategyAgent",
        "choose_parser_tool",
        {
            "file_size": file_size,
            "first_choice": tool_candidates[0],
            "fallback_choices": tool_candidates[1:],
            "file_type": plan["file_type"],
            "reason": plan["reason"],
        },
    )
    return state


def _document_parser_agent(state: PDFIngestionState) -> PDFIngestionState:
    if not os.getenv("ZHIPU_API_KEY"):
        raise RuntimeError("ZHIPU_API_KEY 未配置，无法调用智谱 PDF 解析接口")

    parser = PDFParser()
    tool_type = state.get("current_tool_type") or "lite"
    file_type = state.get("current_file_type") or "PDF"
    try:
        parser_result = parser.parse(state["pdf_file"]["file_path"], file_type=file_type, tool_type=tool_type)
        content = parser_result.get("content") or ""
        state["parser_result"] = parser_result
        state["content"] = content
        state.pop("parse_error", None)
        state.setdefault("parse_attempts", []).append(
            {"tool_type": tool_type, "file_type": file_type, "status": parser_result.get("status"), "content_length": len(content)}
        )
    except Exception as exc:
        state["parse_error"] = str(exc)
        state["content"] = ""
        state.setdefault("parse_attempts", []).append(
            {"tool_type": tool_type, "file_type": file_type, "status": "error", "error": str(exc)}
        )

    _append_trace(
        state,
        "DocumentParserAgent",
        "parse_pdf",
        {
            "tool_type": tool_type,
            "file_type": file_type,
            "status": "error" if state.get("parse_error") else state.get("parser_result", {}).get("status"),
            "content_length": len(state.get("content") or ""),
            "error": state.get("parse_error"),
        },
    )
    return state


def _extraction_quality_agent(state: PDFIngestionState) -> PDFIngestionState:
    content = state.get("content") or ""
    plan = state.get("parser_plan") or {}
    min_content_length = int(plan.get("min_content_length") or 200)
    parse_error = state.get("parse_error")

    missing_fields: list[str] = []
    s_ref = None
    fee_items_count = 0
    if content.strip():
        try:
            parsed = parse_demonstrativo_text(content)
            business = parsed.business or {}
            fee_items_count = len(parsed.fee_items or [])
            s_ref = business.get("s_ref")
            required_fields = plan.get("required_fields") or ["s_ref"]
            missing_fields = [field for field in required_fields if not str(business.get(field) or "").strip()]
        except Exception as exc:
            missing_fields = ["s_ref"]
            _append_trace(state, "ExtractionQualityAgent", "rule_preview_failed", {"error": str(exc)})

    reasons: list[str] = []
    if parse_error:
        reasons.append("parser_error")
    if len(content.strip()) < min_content_length:
        reasons.append("content_too_short")
    if missing_fields:
        reasons.append("missing_core_fields")

    candidates = plan.get("tool_candidates") or []
    current_index = int(plan.get("current_index") or 0)
    has_fallback = current_index < len(candidates) - 1
    status = "RETRY" if reasons and has_fallback else "FAILED" if reasons else "ACCEPT"
    quality = {
        "status": status,
        "reasons": reasons,
        "content_length": len(content),
        "min_content_length": min_content_length,
        "missing_fields": missing_fields,
        "s_ref": s_ref,
        "fee_items_count": fee_items_count,
        "has_fallback": has_fallback,
    }
    state["quality"] = quality
    _append_trace(state, "ExtractionQualityAgent", "assess_parse_quality", quality)
    return state


def _retry_parser_agent(state: PDFIngestionState) -> PDFIngestionState:
    plan = state["parser_plan"]
    candidates = plan.get("tool_candidates") or ["lite"]
    next_index = min(int(plan.get("current_index") or 0) + 1, len(candidates) - 1)
    plan["current_index"] = next_index
    state["parser_plan"] = plan
    state["current_tool_type"] = candidates[next_index]
    state.pop("parse_error", None)
    _append_trace(
        state,
        "RetryParserAgent",
        "escalate_parser_tool",
        {
            "next_tool_type": state["current_tool_type"],
            "previous_quality": state.get("quality"),
            "reason": "quality_agent_requested_retry",
        },
    )
    return state


def _parser_failure_agent(state: PDFIngestionState) -> PDFIngestionState:
    quality = state.get("quality") or {}
    attempts = state.get("parse_attempts") or []
    _append_trace(
        state,
        "ParserStrategyAgent",
        "mark_needs_review",
        {"quality": quality, "attempts": attempts},
    )
    raise RuntimeError(f"PDF 智能体解析失败，需要人工复核。quality={quality}, attempts={attempts}")


def _business_extraction_agent(state: PDFIngestionState) -> PDFIngestionState:
    from services import upsert_business_with_fees

    db = state["db"]
    pdf_file = state["pdf_file"]
    with db.connection() as conn:
        business = upsert_business_with_fees(
            db,
            conn,
            raw_text=state["content"],
            source_file_id=int(pdf_file["id"]),
        )

    state["business"] = business
    _append_trace(
        state,
        "BusinessExtractionAgent",
        "extract_and_upsert_business",
        {
            "business_id": business.get("id"),
            "s_ref": business.get("s_ref"),
            "fee_items_count": len(business.get("fee_items") or []),
        },
    )
    return state


def _field_validation_agent(state: PDFIngestionState) -> PDFIngestionState:
    business = state["business"]
    fee_items = business.get("fee_items") or []
    required_fields = ["s_ref", "invoice_no", "customer_name", "customer_tax_no"]
    missing_fields = [field for field in required_fields if not str(business.get(field) or "").strip()]
    validation = {
        "missing_fields": missing_fields,
        "fee_items_count": len(fee_items),
        "status": "WARN" if missing_fields or not fee_items else "PASS",
    }
    state["validation"] = validation
    _append_trace(state, "FieldValidationAgent", "validate_extracted_fields", validation)
    return state


def _auto_audit_agent(state: PDFIngestionState) -> PDFIngestionState:
    if not state.get("auto_audit"):
        _append_trace(state, "AutoAuditAgent", "skip_auto_audit", {"reason": "auto_audit=false"})
        return state

    from app.services.audit_finance_service import run_audit_review

    business = state["business"]
    try:
        audit = run_audit_review(
            state["db"],
            business_id=int(business["id"]),
            created_by=state.get("created_by"),
        )
        state["audit"] = audit
        _append_trace(
            state,
            "AutoAuditAgent",
            "run_business_audit_agent",
            {"audit_run_id": audit.get("id"), "risk_level": audit.get("risk_level"), "source": audit.get("source")},
        )
    except Exception as exc:
        state["audit_error"] = str(exc)
        _append_trace(state, "AutoAuditAgent", "audit_failed_non_blocking", {"error": str(exc)})
    return state


def _build_pdf_graph():
    try:
        from langgraph.graph import END, StateGraph
    except Exception as exc:
        raise RuntimeError("langgraph 未安装，无法运行 PDF 多智能体流程") from exc

    graph = StateGraph(PDFIngestionState)
    graph.add_node("parser_strategy_agent", _parser_strategy_agent)
    graph.add_node("document_parser_agent", _document_parser_agent)
    graph.add_node("extraction_quality_agent", _extraction_quality_agent)
    graph.add_node("retry_parser_agent", _retry_parser_agent)
    graph.add_node("parser_failure_agent", _parser_failure_agent)
    graph.add_node("business_extraction_agent", _business_extraction_agent)
    graph.add_node("field_validation_agent", _field_validation_agent)
    graph.add_node("auto_audit_agent", _auto_audit_agent)
    graph.set_entry_point("parser_strategy_agent")
    graph.add_edge("parser_strategy_agent", "document_parser_agent")
    graph.add_edge("document_parser_agent", "extraction_quality_agent")
    graph.add_conditional_edges(
        "extraction_quality_agent",
        lambda state: str((state.get("quality") or {}).get("status") or "FAILED").lower(),
        {
            "accept": "business_extraction_agent",
            "retry": "retry_parser_agent",
            "failed": "parser_failure_agent",
        },
    )
    graph.add_edge("retry_parser_agent", "document_parser_agent")
    graph.add_edge("parser_failure_agent", END)
    graph.add_edge("business_extraction_agent", "field_validation_agent")
    graph.add_edge("field_validation_agent", "auto_audit_agent")
    graph.add_edge("auto_audit_agent", END)
    return graph.compile()


def run_pdf_ingestion_agent(
    *,
    db,
    pdf_file: dict[str, Any],
    task: dict[str, Any],
    created_by: int | None = None,
    auto_audit: bool = True,
) -> dict[str, Any]:
    app = _build_pdf_graph()
    final_state = app.invoke(
        {
            "db": db,
            "pdf_file": pdf_file,
            "task": task,
            "created_by": created_by,
            "auto_audit": auto_audit,
            "trace": [
                {
                    "agent": "PDFIngestionSupervisor",
                    "action": "start",
                    "detail": {"file_id": pdf_file.get("id"), "task_id": task.get("id")},
                }
            ],
        }
    )

    result = {
        "file": pdf_file,
        "task_id": task["id"],
        "business": final_state.get("business"),
        "agent_trace": final_state.get("trace", []),
        "task_raw_result": {
            "framework": "langchain_langgraph",
            "parser_plan": final_state.get("parser_plan"),
            "parse_attempts": final_state.get("parse_attempts", []),
            "quality": final_state.get("quality"),
            "parser_result": final_state.get("parser_result"),
            "validation": final_state.get("validation"),
            "agent_trace": final_state.get("trace", []),
        },
    }
    if final_state.get("audit"):
        result["audit"] = final_state["audit"]
    if final_state.get("audit_error"):
        result["audit_error"] = final_state["audit_error"]
    return result
