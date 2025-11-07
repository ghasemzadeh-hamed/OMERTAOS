"""Profile helpers for the control plane."""
from __future__ import annotations

import json
import importlib.util
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Tuple

ROOT_DIR = Path(__file__).resolve().parents[2]
PROFILE_FILE = ROOT_DIR / ".aionos" / "profile.json"
ENV_PATH = ROOT_DIR / ".env"
_VALID_PROFILES = {"user", "professional", "enterprise-vip"}


def _load_profile_module() -> ModuleType:
    module_path = ROOT_DIR / "kernel-multitenant" / "profile_loader.py"
    spec = importlib.util.spec_from_file_location("kernel_profile_loader", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load profile loader from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


def _sync_env_flags(profile: str) -> None:
    os.environ["AION_PROFILE"] = profile
    if profile == "enterprise-vip":
        os.environ["FEATURE_SEAL"] = "1"
    else:
        os.environ["FEATURE_SEAL"] = "0"


def _read_profile_file() -> Tuple[str, bool] | None:
    if PROFILE_FILE.is_file():
        try:
            data = json.loads(PROFILE_FILE.read_text())
            profile = str(data.get("profile", "")).strip().lower()
            if profile in _VALID_PROFILES:
                setup_done = bool(data.get("setupDone", False))
                return profile, setup_done
        except Exception:
            return None
    return None


def _read_env_profile() -> str | None:
    env_profile = os.getenv("AION_PROFILE")
    if env_profile:
        return env_profile.lower()
    if ENV_PATH.is_file():
        for line in ENV_PATH.read_text().splitlines():
            if line.startswith("AION_PROFILE="):
                return line.split("=", 1)[1].strip().lower()
    return None


def _write_env_profile(profile: str) -> None:
    if not ENV_PATH.exists():
        ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
        ENV_PATH.touch()
    lines = []
    with ENV_PATH.open("r", encoding="utf-8") as handle:
        lines = [line.rstrip("\n") for line in handle]
    filtered = [line for line in lines if not line.startswith("AION_PROFILE=") and not line.startswith("FEATURE_SEAL=")]
    filtered.append(f"AION_PROFILE={profile}")
    filtered.append("FEATURE_SEAL=1" if profile == "enterprise-vip" else "FEATURE_SEAL=0")
    with ENV_PATH.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(filtered) + "\n")


def read_profile_state() -> Tuple[str, bool]:
    entry = _read_profile_file()
    if entry is not None:
        profile, setup_done = entry
    else:
        profile = _read_env_profile() or "user"
        setup_done = False
    _sync_env_flags(profile)
    return profile, setup_done


def set_profile_state(profile: str, setup_done: bool = True) -> None:
    profile = profile.lower()
    if profile not in _VALID_PROFILES:
        raise ValueError(f"invalid profile: {profile}")
    PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "profile": profile,
        "setupDone": setup_done,
        "updatedAt": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    }
    PROFILE_FILE.write_text(json.dumps(payload, indent=2))
    _write_env_profile(profile)
    _sync_env_flags(profile)
    load_profile.cache_clear()


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
    profile_name, _ = read_profile_state()
    root_override = os.getenv("AION_ROOT")
    profile = load_profile(profile_name, root=Path(root_override) if root_override else ROOT_DIR)
    return profile_name, profile


__all__ = [
    "get_profile",
    "load_profile",
    "read_profile_state",
    "set_profile_state",
]
