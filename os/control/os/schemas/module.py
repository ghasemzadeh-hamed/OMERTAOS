"""Pydantic models for module manifests."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, constr


class ModuleManifest(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    version: constr(strip_whitespace=True, min_length=1)
    description: Optional[str] = None
    runtime: Optional[dict] = None
    security: Optional[dict] = None


class ModuleOut(ModuleManifest):
    enabled: bool = True

    class Config:
        orm_mode = True
