import os
from typing import Any, Dict

import yaml


def deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for key, value in b.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_profile(profile_name: str, base_dir: str) -> Dict[str, Any]:
    base_path = os.path.join(base_dir, "profiles", "kernel.base.yaml")
    profile_path = os.path.join(base_dir, "profiles", f"kernel.{profile_name}.yaml")
    base_data = yaml.safe_load(open(base_path)) if os.path.exists(base_path) else {}
    profile_data = yaml.safe_load(open(profile_path)) if os.path.exists(profile_path) else {}
    parent_name = profile_data.get("inherits")
    if parent_name:
        parent_data = load_profile(parent_name, base_dir)
        return deep_merge(deep_merge(base_data, parent_data), profile_data)
    return deep_merge(base_data, profile_data)
