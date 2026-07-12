from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import requests


class LLMProviderError(RuntimeError):
    """Raised when an HTTP model provider cannot return a safe response."""


def call_openai_compatible(
    endpoint: str,
    api_key: str | None,
    model: str,
    system: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    temperature: float,
    timeout_ms: int,
) -> str:
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise LLMProviderError("LLM endpoint must be an absolute HTTP(S) URL")
    if timeout_ms <= 0:
        raise LLMProviderError("LLM timeout must be positive")
    if max_tokens <= 0:
        raise LLMProviderError("LLM max_tokens must be positive")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload: dict[str, Any] = {
        "model": model,
        "messages": ([{"role": "system", "content": system}] + messages) if system else messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    response = requests.post(
        endpoint,
        json=payload,
        headers=headers,
        timeout=timeout_ms / 1000,
        allow_redirects=False,
    )  # nosec B113
    if 300 <= response.status_code < 400:
        raise LLMProviderError("LLM provider redirects are not allowed")
    response.raise_for_status()
    data = response.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMProviderError("LLM provider returned an invalid response shape") from exc
    if not isinstance(content, str):
        raise LLMProviderError("LLM provider content must be a string")
    return content
