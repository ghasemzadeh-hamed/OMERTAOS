"""Configuration helpers for AION-OS application packages."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def load_env() -> dict[str, str]:
    """Return a copy of the current process environment."""
    return dict(os.environ)


def get_config(key: str, default: Any = None) -> Any:
    """Read a configuration key from environment variables."""
    if not key:
        return default
    return os.getenv(key, default)


def get_bool(key: str, default: bool = False) -> bool:
    value = get_config(key)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def get_float(key: str, default: float) -> float:
    value = get_config(key)
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def get_path(key: str, default: str | Path | None = None) -> Path | None:
    value = get_config(key)
    if value in (None, ""):
        return Path(default).expanduser() if default is not None else None
    return Path(str(value)).expanduser()


def load_scope(scope_name: str) -> dict[str, Any]:
    """Load a YAML configuration scope from ``config/scopes/<scope_name>.yaml`` if present."""
    scope_file = Path(__file__).resolve().parent / "scopes" / f"{scope_name}.yaml"
    if not scope_file.exists():
        return {}
    with scope_file.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


__all__ = [
    "get_bool",
    "get_config",
    "get_float",
    "get_path",
    "load_env",
    "load_scope",
]
