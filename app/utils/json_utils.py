"""JSON helpers for tolerant parsing."""

from __future__ import annotations

import json
from typing import Any, Dict


def safe_json_parse(content: str) -> Dict[str, Any]:
    """Parse JSON content and fall back to an empty dict on failure."""

    try:
        parsed = json.loads(content)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


__all__ = ["safe_json_parse"]
