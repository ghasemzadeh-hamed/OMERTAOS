"""Pydantic models for provider management."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, HttpUrl, constr


class ProviderBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    kind: constr(strip_whitespace=True, min_length=1)
    base_url: HttpUrl
    models: List[str]
    api_key: Optional[str] = None


class ProviderCreate(ProviderBase):
    pass


class ProviderOut(ProviderBase):
    enabled: bool = True

    class Config:
        orm_mode = True
