from __future__ import annotations

import json
import os
from collections.abc import Iterable

DEFAULT_CORS_ORIGINS = ("http://localhost:3000", "http://127.0.0.1:3000")


def _parse_cors_origins(value: object) -> list[str]:
    defaults = list(DEFAULT_CORS_ORIGINS)
    if value is None:
        return defaults
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return defaults
        if stripped == "*":
            return ["*"]
        if stripped.startswith("["):
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError:
                return defaults
        elif "," in stripped:
            return [part.strip() for part in stripped.split(",") if part.strip()] or defaults
        else:
            return [stripped]
    if isinstance(value, Iterable):
        origins = [str(item).strip() for item in value if str(item).strip()]
        return origins or defaults
    return defaults


class Settings:
    """Minimal canonical Control settings recovered from the removed namespace."""

    def __init__(self) -> None:
        raw_origins = next(
            (
                os.environ[key]
                for key in (
                    "AION_CONTROL_CORS_ORIGINS",
                    "AION_CORS_ORIGINS",
                    "CORS_ORIGINS",
                    "AION_CONSOLE_ORIGIN",
                )
                if key in os.environ
            ),
            None,
        )
        self.cors_origins = _parse_cors_origins(raw_origins)
