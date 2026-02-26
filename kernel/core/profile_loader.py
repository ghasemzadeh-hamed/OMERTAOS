from __future__ import annotations

from pathlib import Path

import yaml


class ProfileLoader:
    def __init__(self, profiles_dir: str = "config/profiles") -> None:
        self._dir = Path(profiles_dir)

    def load(self, profile: str) -> dict[str, object]:
        path = self._dir / f"{profile}.yaml"
        if not path.exists():
            raise FileNotFoundError(path)
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
