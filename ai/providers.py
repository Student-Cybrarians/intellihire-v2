from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Optional

import requests


class AIProviderError(RuntimeError):
    pass


class AIUnavailableError(AIProviderError):
    pass


@dataclass
class AIResponse:
    content: str
    provider: str
    model: str
    request_id: str
    latency_ms: int
    usage: Dict[str, Any]
    raw: Dict[str, Any]


class AIProvider:
    name = "base"

    def generate(self, messages: List[Dict[str, Any]], *, model: str, tools=None,
                 response_format=None, temperature: float = 0.2, max_tokens: int = 2048,
                 timeout: float = 30, reasoning: bool = False) -> AIResponse:
        raise NotImplementedError

    def stream(self, messages: List[Dict[str, Any]], *, model: str, tools=None,
               temperature: float = 0.2, max_tokens: int = 2048,
               timeout: float = 60, reasoning: bool = False) -> Iterator[str]:
        raise NotImplementedError

    def health(self) -> Dict[str, Any]:
        return {"provider": self.name, "configured": False}


class DeepSeekProvider(AIProvider):
    name = "deepseek"

    def __init__(self) -> None:
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
        self.default_model = os.getenv("DEEPSEEK_MODEL", "").strip()
        self.timeout = float(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "30"))

    @property
    def endpoint(self) -> str:
        return self.base_url if self.base_url.endswith("/chat/completions") else self.base_url + "/chat/completions"

    def _payload(self, messages, model, tools, response_format, temperature, max_tokens, stream, reasoning):
        if not model:
            raise AIUnavailableError("DEEPSEEK_MODEL is not configured")
        # Keep the stable prefix deterministic; volatile user context belongs in later messages.
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        if tools:
            payload["tools"] = tools
        if response_format:
            payload["response_format"] = response_format
        # DeepSeek-compatible endpoints vary in their reasoning flag. Only send it when explicitly enabled.
        if reasoning:
            payload["thinking"] = {"type": "enabled"}
        return payload

    def generate(self, messages, *, model, tools=None, response_format=None,
                 temperature=0.2, max_tokens=2048, timeout=30, reasoning=False):
        if not self.api_key:
            raise AIUnavailableError("DEEPSEEK_API_KEY is not configured")
        request_id = str(uuid.uuid4())
        started = time.monotonic()
        payload = self._payload(messages, model or self.default_model, tools, response_format,
                                temperature, max_tokens, False, reasoning)
        try:
            response = requests.post(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=max(1.0, timeout or self.timeout),
            )
            response.raise_for_status()
            body = response.json()
            choice = (body.get("choices") or [{}])[0]
            message = choice.get("message") or {}
            content = message.get("content") or ""
            if not content and choice.get("finish_reason") == "tool_calls":
                content = ""
            return AIResponse(
                content=content,
                provider=self.name,
                model=str(body.get("model") or model or self.default_model),
                request_id=request_id,
                latency_ms=round((time.monotonic() - started) * 1000),
                usage=body.get("usage") or {},
                raw=body,
            )
        except requests.RequestException as exc:
            raise AIProviderError(f"DeepSeek request failed: {type(exc).__name__}: {exc}") from exc
        except (ValueError, KeyError, TypeError) as exc:
            raise AIProviderError(f"DeepSeek returned an invalid response: {type(exc).__name__}") from exc

    def stream(self, messages, *, model, tools=None, temperature=0.2, max_tokens=2048,
               timeout=60, reasoning=False):
        if not self.api_key:
            raise AIUnavailableError("DEEPSEEK_API_KEY is not configured")
        payload = self._payload(messages, model or self.default_model, tools, None,
                                temperature, max_tokens, True, reasoning)
        try:
            with requests.post(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=max(1.0, timeout or self.timeout),
                stream=True,
            ) as response:
                response.raise_for_status()
                for raw_line in response.iter_lines(decode_unicode=True):
                    if not raw_line:
                        continue
                    line = raw_line.strip()
                    if line.startswith("data:"):
                        line = line[5:].strip()
                    if line == "[DONE]":
                        break
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    choices = chunk.get("choices") or []
                    if not choices:
                        continue
                    delta = choices[0].get("delta") or {}
                    content = delta.get("content")
                    if content:
                        yield str(content)
        except requests.RequestException as exc:
            raise AIProviderError(f"DeepSeek stream failed: {type(exc).__name__}: {exc}") from exc

    def health(self):
        return {
            "provider": self.name,
            "configured": bool(self.api_key and self.default_model),
            "model_configured": bool(self.default_model),
            "base_url": self.base_url,
        }


class DeepSeekHarnessAdapter(DeepSeekProvider):
    """Isolation point for a verified deepseek-harness implementation.

    The requested deepseek-ai/deepseek-harness repository could not be verified.
    This adapter therefore does not import or silently substitute another harness.
    It delegates to the official OpenAI-compatible DeepSeek transport until a
    verified harness is explicitly configured.
    """
    name = "deepseek-harness-adapter"


def build_provider_chain() -> Dict[str, AIProvider]:
    providers: Dict[str, AIProvider] = {"deepseek": DeepSeekProvider()}
    return providers
