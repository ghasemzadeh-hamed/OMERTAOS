"""Versioned module manifest schemas."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, constr


class ModuleManifest(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    version: constr(strip_whitespace=True, min_length=1)
    description: Optional[str] = None
    runtime: Optional[dict] = None
    security: Optional[dict] = None


class ModuleOut(ModuleManifest):
    model_config = ConfigDict(from_attributes=True)

    enabled: bool = True
