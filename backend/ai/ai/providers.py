from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List

import requests


class AIProviderError(RuntimeError):
    pass


class AIUnavailableError(AIProviderError):
    pass


class AIProviderTimeoutError(AIProviderError):
    """Raised when a provider does not respond within the configured timeout."""
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


class OpenAICompatibleProvider(AIProvider):
    """Small requests-based adapter for OpenAI-compatible chat APIs."""

    api_key_env = ""
    model_env = ""
    default_base_url = ""

    def __init__(self) -> None:
        self.api_key = os.getenv(self.api_key_env, "").strip()
        self.base_url = os.getenv(f"{self.name.upper()}_BASE_URL", self.default_base_url).rstrip("/")
        self.default_model = os.getenv(self.model_env, "").strip()

    @property
    def endpoint(self) -> str:
        return self.base_url if self.base_url.endswith("/chat/completions") else self.base_url + "/chat/completions"

    def _payload(self, messages, model, tools, response_format, temperature, max_tokens, stream, reasoning):
        if not model:
            raise AIUnavailableError(f"{self.model_env} is not configured")
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
        if reasoning:
            payload["thinking"] = {"type": "enabled"}
        return payload

    def generate(self, messages, *, model, tools=None, response_format=None,
                 temperature=0.2, max_tokens=2048, timeout=30, reasoning=False):
        if not self.api_key:
            raise AIUnavailableError(f"{self.api_key_env} is not configured")
        request_id = str(uuid.uuid4())
        started = time.monotonic()
        payload = self._payload(messages, model or self.default_model, tools, response_format,
                                temperature, max_tokens, False, reasoning)
        try:
            response = requests.post(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=max(1.0, timeout),
            )
            response.raise_for_status()
            body = response.json()
            choice = (body.get("choices") or [{}])[0]
            message = choice.get("message") or {}
            return AIResponse(
                content=message.get("content") or "",
                provider=self.name,
                model=str(body.get("model") or model or self.default_model),
                request_id=request_id,
                latency_ms=round((time.monotonic() - started) * 1000),
                usage=body.get("usage") or {},
                raw=body,
            )
        except requests.Timeout as exc:
            raise AIProviderTimeoutError(f"{self.name} timed out after {timeout}s") from exc
        except requests.RequestException as exc:
            raise AIProviderError(f"{self.name} request failed: {type(exc).__name__}: {exc}") from exc
        except (ValueError, KeyError, TypeError) as exc:
            raise AIProviderError(f"{self.name} returned an invalid response: {type(exc).__name__}") from exc

    def stream(self, messages, *, model, tools=None, temperature=0.2, max_tokens=2048,
               timeout=60, reasoning=False):
        if not self.api_key:
            raise AIUnavailableError(f"{self.api_key_env} is not configured")
        payload = self._payload(messages, model or self.default_model, tools, None,
                                temperature, max_tokens, True, reasoning)
        try:
            with requests.post(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=(min(10.0, max(1.0, timeout)), max(1.0, timeout)),
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
        except requests.Timeout as exc:
            raise AIProviderTimeoutError(f"{self.name} stream timed out after {timeout}s") from exc
        except requests.RequestException as exc:
            raise AIProviderError(f"{self.name} stream failed: {type(exc).__name__}: {exc}") from exc

    def health(self):
        return {
            "provider": self.name,
            "configured": bool(self.api_key and self.default_model),
            "model_configured": bool(self.default_model),
            "base_url": self.base_url,
        }


class DeepSeekProvider(OpenAICompatibleProvider):
    name = "deepseek"
    api_key_env = "DEEPSEEK_API_KEY"
    model_env = "DEEPSEEK_MODEL"
    default_base_url = "https://api.deepseek.com"


class OpenAIProvider(OpenAICompatibleProvider):
    name = "openai"
    api_key_env = "OPENAI_API_KEY"
    model_env = "OPENAI_MODEL"
    default_base_url = "https://api.openai.com/v1"


class NvidiaProvider(OpenAICompatibleProvider):
    name = "nvidia"
    api_key_env = "NVIDIA_API_KEY"
    model_env = "NVIDIA_MODEL"
    default_base_url = "https://integrate.api.nvidia.com/v1"


class DeepSeekHarnessAdapter(DeepSeekProvider):
    """Isolation point for a verified deepseek-harness implementation."""
    name = "deepseek-harness-adapter"


def build_provider_chain() -> Dict[str, AIProvider]:
    # Providers are instantiated once; the orchestrator decides which configured
    # provider gets the request. No browser-visible API keys are used.
    return {
        "deepseek": DeepSeekProvider(),
        "openai": OpenAIProvider(),
        "nvidia": NvidiaProvider(),
    }
