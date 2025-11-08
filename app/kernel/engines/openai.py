"""Minimal OpenAI Chat Completions client."""

from __future__ import annotations

import os
from typing import List, Mapping

import requests


class OpenAIChat:
    """Invoke OpenAI compatible chat completions endpoints."""

    def __init__(
        self,
        model: str,
        temperature: float = 0.2,
        base_url: str | None = None,
        timeout: int = 60,
    ) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self.model = model
        self.temperature = temperature
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.timeout = timeout

    @staticmethod
    def is_available() -> bool:
        return bool(os.getenv("OPENAI_API_KEY"))

    def complete(self, messages: List[Mapping[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": list(messages),
            "temperature": self.temperature,
            "stream": False,
        }
        response = requests.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        body = response.json()
        choices = body.get("choices") or []
        if not choices:
            raise RuntimeError("OpenAI response did not contain choices")
        message = choices[0].get("message") or {}
        return str(message.get("content", ""))
