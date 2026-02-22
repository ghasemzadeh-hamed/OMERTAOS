from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def load_env() -> dict[str, str]:
    """Return current process environment as a plain mapping."""
    return dict(os.environ)


def get_config(key: str, default: Any = None) -> Any:
    """Read a config value from environment with optional default."""
    return os.environ.get(key, default)


def get_bool(key: str, default: bool = False) -> bool:
    """Return an environment-backed boolean.

    Truthy values: 1,true,yes,on (case-insensitive).
    Falsy values: 0,false,no,off,empty.
    """
    value = os.environ.get(key)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off", ""}:
        return False
    return default


def get_float(key: str, default: float) -> float:
    """Return an environment-backed float with safe fallback."""
    raw = os.environ.get(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def get_path(key: str, default: str | Path) -> Path:
    """Return a normalized path from env or provided default."""
    value = os.environ.get(key)
    candidate = Path(value) if value else Path(default)
    return candidate.expanduser()


def _resolve_env_tokens(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        body = value[2:-1]
        if ":-" in body:
            var, fallback = body.split(":-", 1)
            return os.environ.get(var, fallback)
        return os.environ.get(body, "")
    if isinstance(value, dict):
        return {k: _resolve_env_tokens(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_tokens(v) for v in value]
    return value


def load_scope(scope_name: str, *, base_path: str | Path | None = None) -> dict[str, Any]:
    """Load a YAML scope and resolve ${ENV} tokens recursively."""
    base = Path(base_path) if base_path else Path.cwd()
    path = Path(scope_name)
    if not path.is_absolute():
        path = base / scope_name
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return _resolve_env_tokens(data)
