"""LLM client wrapper supporting API, local, and disabled providers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests


class LLMProviderDisabled(Exception):
    """Raised when the configured LLM provider is disabled or unavailable."""


__all__ = ["LLMProviderDisabled", "call_llm"]


def call_llm_via_api(
    endpoint: str,
    api_key: Optional[str],
    model: str,
    system: str,
    messages: List[Dict[str, str]],
    max_tokens: int,
    temperature: float,
    timeout_ms: int,
) -> str:
    if not endpoint or endpoint == "disabled":
        raise LLMProviderDisabled("LLM endpoint is disabled")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload: Dict[str, Any] = {
        "model": model,
        "messages": ([{"role": "system", "content": system}] + messages) if system else messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout_ms / 1000)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def call_llm(
    provider_cfg: Dict[str, Any],
    system: str,
    messages: List[Dict[str, str]],
    max_tokens: int,
    temperature: float,
) -> str:
    provider = provider_cfg.get("provider", "api")
    endpoint = provider_cfg.get("endpoint", "")
    model = provider_cfg.get("model", "")
    api_key = provider_cfg.get("api_key")
    timeout_ms = int(provider_cfg.get("timeout_ms", 10000))

    if provider in {"api", "local"}:
        return call_llm_via_api(
            endpoint=endpoint,
            api_key=api_key if provider == "api" else None,
            model=model,
            system=system,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout_ms=timeout_ms,
        )

    if provider == "disabled":
        raise LLMProviderDisabled("Provider is disabled")

    raise LLMProviderDisabled(f"Unknown provider: {provider}")
