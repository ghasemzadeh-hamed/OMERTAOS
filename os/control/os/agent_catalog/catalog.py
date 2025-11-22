"""Utilities to load the static agent catalog and recipes."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import ValidationError

from os.control.os.core.logger import get_logger
from os.control.os.schemas.agent import AgentTemplate

LOGGER = get_logger(__name__)


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
            return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        LOGGER.warning("agent catalog missing", extra={"path": str(path)})
        return {}
    except yaml.YAMLError as exc:
        LOGGER.warning("invalid agent catalog yaml", extra={"path": str(path), "error": str(exc)})
        return {}


class AgentCatalog:
    """Load agent templates and recipes from disk."""

    def __init__(self, root: Path | None = None) -> None:
        base = Path(root) if root else Path(os.getenv("AION_AGENT_CATALOG_DIR", "config/agent_catalog"))
        self._root = base.resolve()
        self._catalog_path = self._root / "agents.yaml"

    def list_templates(self) -> List[AgentTemplate]:
        payload = _load_yaml(self._catalog_path)
        templates: List[AgentTemplate] = []
        for raw in payload.get("agents", []):
            if not isinstance(raw, dict):
                continue
            try:
                template = AgentTemplate(**raw)
            except ValidationError as exc:
                LOGGER.warning("invalid agent template", extra={"error": str(exc), "template": raw})
                continue
            templates.append(template)
        return templates

    def get_template(self, template_id: str) -> Optional[AgentTemplate]:
        entries = self.list_templates()
        for template in entries:
            if template.id == template_id:
                return template
        return None

    def load_recipe(self, recipe_path: str) -> Dict[str, Any]:
        resolved = self._root / recipe_path
        if not resolved.exists():
            LOGGER.warning("recipe not found", extra={"recipe": recipe_path})
            return {}
        try:
            with resolved.open("r", encoding="utf-8") as handle:
                content = yaml.safe_load(handle) or {}
                return content if isinstance(content, dict) else {}
        except yaml.YAMLError as exc:
            LOGGER.warning("invalid recipe yaml", extra={"recipe": recipe_path, "error": str(exc)})
            return {}
