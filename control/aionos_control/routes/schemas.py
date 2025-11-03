"""Pydantic schemas for plugin routing."""
from typing import Any, Dict, Optional

from pydantic import BaseModel


class PluginCallRequest(BaseModel):
    """Payload for invoking a plugin entry point."""

    name: str
    params: Optional[Dict[str, Any]] = None
