"""Shared utilities that are reused by installers and runtime services."""

from __future__ import annotations

from .configuration import (
    ensure_config_dirs,
    get_config_root,
    get_profiles_dir,
    get_templates_dir,
    load_env_template,
    write_env_file,
)
from .profiles import (
    AVAILABLE_PROFILES,
    ProfileData,
    detect_profile_name,
    load_profile,
    render_profile_env,
)

__all__ = [
    "AVAILABLE_PROFILES",
    "ProfileData",
    "detect_profile_name",
    "ensure_config_dirs",
    "get_config_root",
    "get_profiles_dir",
    "get_templates_dir",
    "load_env_template",
    "load_profile",
    "render_profile_env",
    "write_env_file",
]
