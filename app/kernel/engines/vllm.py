"""Client for vLLM served chat models."""

from __future__ import annotations

import os
from typing import List, Mapping

import requests


class VLLMChat:
    """Call a vLLM OpenAI-compatible endpoint."""

    def __init__(self, model: str, endpoint: str | None = None, temperature: float = 0.2, timeout: int = 60) -> None:
        self.model = model
        self.endpoint = (endpoint or os.getenv("VLLM_ENDPOINT", "")).rstrip("/")
        if not self.endpoint:
            raise RuntimeError("VLLM_ENDPOINT is not configured")
        self.temperature = temperature
        self.timeout = timeout

    @staticmethod
    def is_available() -> bool:
        endpoint = os.getenv("VLLM_ENDPOINT", "").rstrip("/")
        if not endpoint:
            return False
        try:
            response = requests.get(f"{endpoint}/v1/models", timeout=2)
            return response.status_code < 500
        except Exception:
            return False

    def complete(self, messages: List[Mapping[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": list(messages),
            "temperature": self.temperature,
            "stream": False,
        }
        response = requests.post(f"{self.endpoint}/v1/chat/completions", json=payload, timeout=self.timeout)
        response.raise_for_status()
        body = response.json()
        choices = body.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        return str(message.get("content", ""))
