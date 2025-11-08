"""Client for the Ollama local model runtime."""

from __future__ import annotations

import os
from typing import List, Mapping

import requests


class OllamaChat:
    """Call the Ollama chat API."""

    def __init__(self, model: str, host: str | None = None, temperature: float = 0.2, timeout: int = 60) -> None:
        self.model = model
        self.host = (host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.temperature = temperature
        self.timeout = timeout

    @staticmethod
    def is_available() -> bool:
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        try:
            response = requests.get(f"{host}/api/tags", timeout=2)
            return response.status_code < 500
        except Exception:
            return False

    def complete(self, messages: List[Mapping[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": list(messages),
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        response = requests.post(f"{self.host}/api/chat", json=payload, timeout=self.timeout)
        response.raise_for_status()
        body = response.json()
        message = body.get("message") or {}
        return str(message.get("content", ""))
