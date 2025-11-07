"""Profile configuration loader for AION-OS kernels."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

BASE_DIR = Path(__file__).resolve().parents[2]


def _env_expand(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        key = value[2:-1]
        return os.getenv(key, "")
    if isinstance(value, str):
        result = value
        start = 0
        while True:
            marker = result.find("${", start)
            if marker == -1:
                break
            end_marker = result.find("}", marker)
            if end_marker == -1:
                break
            key = result[marker + 2 : end_marker]
            result = result[:marker] + os.getenv(key, "") + result[end_marker + 1 :]
            start = marker
        return result
    return value


def _expand_env_in_dict(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {key: _expand_env_in_dict(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [_expand_env_in_dict(item) for item in payload]
    return _env_expand(payload)


def load_profile_config(profile_name: str) -> Dict[str, Any]:
    """Load a kernel profile configuration file from disk."""

    candidates = [
        BASE_DIR / "config" / "dev" / "kernel" / f"{profile_name}.yaml",
        BASE_DIR / "config" / "kernel" / f"{profile_name}.yaml",
    ]
    for candidate in candidates:
        if candidate.is_file():
            with candidate.open("r", encoding="utf-8") as handle:
                raw = yaml.safe_load(handle) or {}
            return _expand_env_in_dict(raw)
    return {}


__all__ = ["load_profile_config"]
