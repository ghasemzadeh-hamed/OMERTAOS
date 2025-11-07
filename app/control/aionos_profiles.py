"""Profile helpers for the control plane."""
from __future__ import annotations

import importlib.util
import os
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Tuple

ROOT_DIR = Path(__file__).resolve().parents[2]


def _load_profile_module() -> ModuleType:
    module_path = ROOT_DIR / "kernel-multitenant" / "profile_loader.py"
    spec = importlib.util.spec_from_file_location("kernel_profile_loader", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load profile loader from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


@lru_cache(maxsize=1)
def _profile_module() -> ModuleType:
    return _load_profile_module()


@lru_cache(maxsize=16)
def load_profile(name: str, root: str | Path | None = None) -> Dict[str, Any]:
    module = _profile_module()
    loader = getattr(module, "load_profile")
    base_root = Path(root) if root is not None else ROOT_DIR
    return loader(name, root=base_root)


def get_profile() -> Tuple[str, Dict[str, Any]]:
    profile_name = os.getenv("AION_PROFILE", "user").lower()
    root_override = os.getenv("AION_ROOT")
    profile = load_profile(profile_name, root=Path(root_override) if root_override else ROOT_DIR)
    return profile_name, profile


__all__ = ["get_profile", "load_profile"]
