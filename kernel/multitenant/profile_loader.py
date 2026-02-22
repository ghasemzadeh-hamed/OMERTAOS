"""Profile loading utilities for multi-kernel runtime."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


def deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge dictionaries preserving nested mappings."""
    out: Dict[str, Any] = dict(a)
    for key, value in b.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_profile(name: str, root: str | Path = ".") -> Dict[str, Any]:
    """Load a profile definition, honoring optional inheritance."""
    base_dir = Path(root)
    candidates = [
        base_dir / "profiles",
        base_dir / "config" / "profiles",
        base_dir / "kernel-multitenant" / "profiles",
    ]
    profiles_dir = None
    for candidate in candidates:
        if (candidate / "kernel.base.yaml").exists():
            profiles_dir = candidate
            break
    if profiles_dir is None:
        raise FileNotFoundError("Unable to locate kernel profiles directory")
    base_path = profiles_dir / "kernel.base.yaml"
    profile_path = profiles_dir / f"kernel.{name}.yaml"

    base = yaml.safe_load(base_path.read_text())
    profile = yaml.safe_load(profile_path.read_text())

    parent_name = profile.get("inherits")
    if parent_name:
        parent = load_profile(parent_name, root=base_dir)
        return deep_merge(deep_merge(base, parent), profile)
    return deep_merge(base, profile)


__all__ = ["deep_merge", "load_profile"]
