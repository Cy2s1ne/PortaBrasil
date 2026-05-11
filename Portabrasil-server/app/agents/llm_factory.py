import json
import os
from typing import Any


DEFAULT_PROVIDER = (os.getenv("LLM_PROVIDER") or "qwen").strip().lower()
DEFAULT_QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
DEFAULT_QWEN_BASE_URL = (os.getenv("QWEN_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1").strip().rstrip("/")
DEFAULT_DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
DEFAULT_DEEPSEEK_BASE_URL = (os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com").strip().rstrip("/")
DEFAULT_ZHIPU_MODEL = os.getenv("ZHIPU_LLM_MODEL", "glm-4-flash")
DEFAULT_ZHIPU_BASE_URL = (os.getenv("ZHIPU_BASE_URL") or "https://open.bigmodel.cn/api/paas/v4").strip().rstrip("/")


class LangChainUnavailable(RuntimeError):
    pass


def _provider_config(provider: str | None = None, model: str | None = None) -> dict[str, Any]:
    selected = (provider or DEFAULT_PROVIDER).strip().lower()
    if selected == "qwen":
        return {
            "provider": "qwen",
            "api_key": os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY"),
            "base_url": DEFAULT_QWEN_BASE_URL,
            "model": model or DEFAULT_QWEN_MODEL,
        }
    if selected == "deepseek":
        return {
            "provider": "deepseek",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "base_url": DEFAULT_DEEPSEEK_BASE_URL,
            "model": model or DEFAULT_DEEPSEEK_MODEL,
        }
    if selected == "zhipu":
        return {
            "provider": "zhipu",
            "api_key": os.getenv("ZHIPU_API_KEY"),
            "base_url": DEFAULT_ZHIPU_BASE_URL,
            "model": model or DEFAULT_ZHIPU_MODEL,
        }
    return {"provider": selected, "api_key": None, "base_url": None, "model": model}


def is_langchain_llm_enabled(provider: str | None = None) -> bool:
    config = _provider_config(provider)
    return bool(config.get("api_key") and config.get("base_url") and config.get("model"))


def build_chat_model(
    *,
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 4096,
):
    try:
        from langchain_openai import ChatOpenAI
    except Exception as exc:
        raise LangChainUnavailable("langchain-openai 未安装，无法构建 LangChain ChatModel") from exc

    config = _provider_config(provider, model)
    if not config.get("api_key"):
        raise RuntimeError(f"{config['provider']} API Key 未配置，无法运行 LangChain Agent")
    if not config.get("base_url"):
        raise RuntimeError(f"{config['provider']} base_url 未配置，无法运行 LangChain Agent")

    return ChatOpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
        model=config["model"],
        temperature=temperature,
        max_tokens=max_tokens,
    )


def complete_json_with_langchain(
    *,
    system_prompt: str,
    user_payload: dict[str, Any],
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 4096,
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.messages import HumanMessage, SystemMessage
    except Exception as exc:
        raise LangChainUnavailable("langchain-core 未安装，无法运行 LangChain JSON Chain") from exc

    config = _provider_config(provider, model)
    llm = build_chat_model(
        provider=config["provider"],
        model=config["model"],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    payload_text = json.dumps(user_payload, ensure_ascii=False, default=str)
    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=payload_text),
        ]
    )
    parsed = JsonOutputParser().invoke(response)
    if not isinstance(parsed, dict):
        raise ValueError("LangChain 返回 JSON 顶层必须是对象")

    meta = {
        "framework": "langchain",
        "provider": config["provider"],
        "model": config["model"],
    }
    return parsed, meta
