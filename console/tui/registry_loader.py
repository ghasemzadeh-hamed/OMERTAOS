"""Shared loader for the UI registry so TUI mirrors the web console navigation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


REGISTRY_ROOT = Path(__file__).resolve().parents[2] / "packages" / "ui-core" / "registry"


def load_navigation() -> List[Dict[str, Any]]:
  path = REGISTRY_ROOT / "navigation.json"
  with path.open("r", encoding="utf-8") as handle:
    return json.load(handle)


def load_dashboard_page() -> Dict[str, Any]:
  path = REGISTRY_ROOT / "pages" / "dashboard.page.json"
  with path.open("r", encoding="utf-8") as handle:
    return json.load(handle)
