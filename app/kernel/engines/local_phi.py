"""Ultra-lightweight fallback responder when no external model is available."""

from __future__ import annotations

from typing import List, Mapping


class PhiMini:
    """Return deterministic summaries without requiring model weights."""

    name = "local:phi-3-mini"

    def __init__(self) -> None:
        self.temperature = 0.0

    @staticmethod
    def is_available() -> bool:
        return True

    def complete(self, messages: List[Mapping[str, str]]) -> str:
        if not messages:
            return "FINAL: نمی‌توانم پاسخی ارائه دهم."
        last = messages[-1]
        content = last.get("content", "").strip()
        if not content:
            return "FINAL: لطفاً سوال خود را بیان کن."
        summary = content[:200]
        return (
            "THOUGHT: پاسخ از مدل محلی ساده ساخته شد.\n"
            f"FINAL: {summary}"
        )
