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
            return "FINAL: \u0646\u0645\u06cc\u200c\u062a\u0648\u0627\u0646\u0645 \u067e\u0627\u0633\u062e\u06cc \u0627\u0631\u0627\u0626\u0647 \u062f\u0647\u0645."
        last = messages[-1]
        content = last.get("content", "").strip()
        if not content:
            return "FINAL: \u0644\u0637\u0641\u0627\u064b \u0633\u0648\u0627\u0644 \u062e\u0648\u062f \u0631\u0627 \u0628\u06cc\u0627\u0646 \u06a9\u0646."
        summary = content[:200]
        return (
            "THOUGHT: \u067e\u0627\u0633\u062e \u0627\u0632 \u0645\u062f\u0644 \u0645\u062d\u0644\u06cc \u0633\u0627\u062f\u0647 \u0633\u0627\u062e\u062a\u0647 \u0634\u062f.\n"
            f"FINAL: {summary}"
        )
