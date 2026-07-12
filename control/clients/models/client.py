from __future__ import annotations

from typing import Any

from integrations.providers import LLMProviderError, call_openai_compatible


class LLMProviderDisabled(LLMProviderError):
    """Raised when the selected model provider is disabled or unknown."""


def call_llm_via_api(
    endpoint: str,
    api_key: str | None,
    model: str,
    system: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    temperature: float,
    timeout_ms: int,
) -> str:
    if not endpoint or endpoint == "disabled":
        raise LLMProviderDisabled("LLM endpoint is disabled")
    return call_openai_compatible(
        endpoint,
        api_key,
        model,
        system,
        messages,
        max_tokens,
        temperature,
        timeout_ms,
    )


def call_llm(
    provider_cfg: dict[str, Any],
    system: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    temperature: float,
) -> str:
    provider = provider_cfg.get("provider", "api")
    endpoint = str(provider_cfg.get("endpoint", ""))
    model = str(provider_cfg.get("model", ""))
    api_key = provider_cfg.get("api_key")
    timeout_ms = int(provider_cfg.get("timeout_ms", 10000))

    if provider in {"api", "local"}:
        return call_llm_via_api(
            endpoint=endpoint,
            api_key=str(api_key) if provider == "api" and api_key else None,
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
