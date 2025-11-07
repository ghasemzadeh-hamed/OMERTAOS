"""Shared installer utilities reused across ISO, Linux, and Windows flows."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from app.shared import (
    AVAILABLE_PROFILES,
    detect_profile_name,
    ensure_config_dirs,
    get_config_root,
    get_profiles_dir,
    get_templates_dir,
    load_env_template,
    load_profile,
    render_profile_env,
    write_env_file,
)

__all__ = [
    "AVAILABLE_PROFILES",
    "apply_profile",
    "detect_profile_name",
    "ensure_config_dirs",
    "get_config_root",
    "get_profiles_dir",
    "get_templates_dir",
]


def apply_profile(
    name: str,
    *,
    root: Path | None = None,
    env_path: Path | None = None,
    extra_env: Mapping[str, str] | None = None,
) -> Path:
    """Render the repository's ``.env`` using the requested profile."""

    repo_root = Path(root) if root else Path.cwd()
    ensure_config_dirs(repo_root)

    profile = load_profile(name, repo_root)
    template = load_env_template(repo_root)
    rendered = render_profile_env(profile, template, extra_env=extra_env)

    target = env_path or repo_root / ".env"
    write_env_file(rendered, target)
    return target
