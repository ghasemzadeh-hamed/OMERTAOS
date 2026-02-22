"""Profile loading helpers shared by installers and the CLI."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, Mapping, MutableMapping

import yaml

from .configuration import get_profiles_dir

ProfileData = Dict[str, object]

AVAILABLE_PROFILES = ("user", "pro", "enterprise")
_PROFILE_FILE_MAP = {
    "user": "kernel.user.yaml",
    "professional": "kernel.pro.yaml",
    "pro": "kernel.pro.yaml",
    "enterprise": "kernel.ent.yaml",
    "enterprise-vip": "kernel.ent.yaml",
}


class ProfileNotFoundError(FileNotFoundError):
    """Raised when a requested profile definition cannot be located."""


def _normalise_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower())


def load_profile(name: str, root: Path | None = None) -> ProfileData:
    normalised = _normalise_name(name)
    filename = _PROFILE_FILE_MAP.get(normalised)
    if filename is None:
        raise ProfileNotFoundError(f"unknown profile: {name}")
    profile_path = get_profiles_dir(root) / filename
    if not profile_path.exists():
        raise ProfileNotFoundError(f"profile file not found: {profile_path}")
    with profile_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, MutableMapping):
        raise ValueError(f"profile file {profile_path} did not produce a mapping")
    data.setdefault("name", normalised)
    return dict(data)


def detect_profile_name(env_file: Path) -> str | None:
    if not env_file.exists():
        return None
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("AION_PROFILE="):
            return line.split("=", 1)[1].strip()
    return None


def render_profile_env(
    profile: Mapping[str, object],
    template: str,
    *,
    extra_env: Mapping[str, str] | None = None,
) -> str:
    replacements = {
        "AION_PROFILE": str(profile.get("name", "user")),
        "FEATURE_SEAL": "1" if _profile_enables_seal(profile) else "0",
    }
    if extra_env:
        replacements.update({k: str(v) for k, v in extra_env.items()})

    rendered_lines = []
    seen_keys = set()
    for raw in template.splitlines():
        key = _extract_key(raw)
        if key and key in replacements:
            rendered_lines.append(f"{key}={replacements[key]}")
            seen_keys.add(key)
        else:
            rendered_lines.append(raw)

    for key, value in replacements.items():
        if key not in seen_keys:
            rendered_lines.append(f"{key}={value}")

    return "\n".join(rendered_lines) + "\n"


def _extract_key(line: str) -> str | None:
    if line.lstrip().startswith("#") or "=" not in line:
        return None
    return line.split("=", 1)[0].strip()


def _profile_enables_seal(profile: Mapping[str, object]) -> bool:
    name = str(profile.get("name", "")).lower()
    if "ent" in name:
        return True
    features = profile.get("features")
    if isinstance(features, Mapping):
        seal = features.get("seal")
        if isinstance(seal, Mapping):
            return bool(seal.get("enabled", False))
        if isinstance(seal, bool):
            return seal
    return False
