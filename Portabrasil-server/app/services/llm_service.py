import json
import os
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from zai import ZhipuAiClient


DEFAULT_PROVIDER = (os.getenv("LLM_PROVIDER") or "qwen").strip().lower()
DEFAULT_ZHIPU_MODEL = os.getenv("ZHIPU_LLM_MODEL", "glm-4-flash")
DEFAULT_QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
DEFAULT_QWEN_BASE_URL = (os.getenv("QWEN_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1").strip().rstrip("/")


def _extract_json_text(text: str) -> str:
    candidate = (text or "").strip()
    if not candidate:
        raise ValueError("LLM 返回内容为空")

    if candidate.startswith("{") and candidate.endswith("}"):
        return candidate

    fenced = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", candidate, flags=re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end != -1 and end > start:
        return candidate[start : end + 1].strip()

    raise ValueError("LLM 返回内容中未找到合法 JSON")


def _loads_json_safely(text: str) -> dict[str, Any]:
    raw = _extract_json_text(text)
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("LLM JSON 顶层必须是对象")
    return data


class LLMService:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        provider: str | None = None,
    ):
        self.provider = (provider or DEFAULT_PROVIDER).strip().lower()
        self.client = None
        self.base_url = None

        if self.provider == "qwen":
            self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")
            self.model = model or DEFAULT_QWEN_MODEL
            self.base_url = DEFAULT_QWEN_BASE_URL
        elif self.provider == "zhipu":
            self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
            self.model = model or DEFAULT_ZHIPU_MODEL
            self.client = ZhipuAiClient(api_key=self.api_key) if self.api_key else None
        else:
            self.api_key = api_key
            self.model = model or DEFAULT_QWEN_MODEL

    @property
    def enabled(self) -> bool:
        if self.provider == "qwen":
            return bool(self.api_key and self.base_url)
        if self.provider == "zhipu":
            return bool(self.client and self.api_key)
        return False

    def _complete_json_with_qwen(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1800,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError("DASHSCOPE_API_KEY 未配置，无法调用千问模型")
        if not self.base_url:
            raise RuntimeError("QWEN_BASE_URL 未配置")

        endpoint = f"{self.base_url}/chat/completions"
        payload = {
            "model": model or self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(user_payload, ensure_ascii=False, default=str),
                },
            ],
        }

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        request = Request(endpoint, data=body, headers=headers, method="POST")

        try:
            with urlopen(request, timeout=90) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            try:
                error_text = exc.read().decode("utf-8")
            except Exception:
                error_text = str(exc)
            raise RuntimeError(f"千问调用失败: {error_text}") from exc
        except URLError as exc:
            raise RuntimeError(f"千问网络请求失败: {exc}") from exc

        try:
            data = json.loads(raw)
        except Exception as exc:
            raise RuntimeError(f"千问返回内容不是合法 JSON: {raw[:200]}") from exc

        if isinstance(data.get("error"), dict):
            message = data["error"].get("message") or str(data["error"])
            raise RuntimeError(f"千问返回错误: {message}")

        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError("千问未返回候选结果")
        message = choices[0].get("message") or {}
        content = message.get("content")

        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict):
                    text_parts.append(str(part.get("text") or ""))
                else:
                    text_parts.append(str(part))
            content = "".join(text_parts).strip()

        if isinstance(content, dict):
            parsed = content
        else:
            parsed = _loads_json_safely(str(content or ""))

        meta = {
            "provider": "qwen",
            "model": data.get("model") or model or self.model,
            "request_id": data.get("id"),
            "usage": data.get("usage"),
        }
        return parsed, meta

    def _complete_json_with_zhipu(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1800,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.client:
            raise RuntimeError("ZHIPU_API_KEY 未配置，无法调用智谱大模型")

        response = self.client.chat.completions.create(
            model=model or self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(user_payload, ensure_ascii=False, default=str),
                },
            ],
        )

        choices = getattr(response, "choices", None) or []
        if not choices:
            raise RuntimeError("LLM 未返回候选结果")

        message = getattr(choices[0], "message", None)
        content = getattr(message, "content", None) if message else None
        if not content:
            raise RuntimeError("LLM 返回内容为空")

        parsed = _loads_json_safely(content)
        meta = {
            "provider": "zhipu",
            "model": getattr(response, "model", None) or model or self.model,
            "request_id": getattr(response, "request_id", None),
            "usage": getattr(getattr(response, "usage", None), "model_dump", lambda: None)(),
        }
        return parsed, meta

    def complete_json(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1800,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.enabled:
            raise RuntimeError(f"当前 LLM provider={self.provider} 未就绪，请检查 API Key 配置")

        if self.provider == "qwen":
            return self._complete_json_with_qwen(
                system_prompt=system_prompt,
                user_payload=user_payload,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        if self.provider == "zhipu":
            return self._complete_json_with_zhipu(
                system_prompt=system_prompt,
                user_payload=user_payload,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        raise RuntimeError(f"不支持的 LLM provider: {self.provider}")
