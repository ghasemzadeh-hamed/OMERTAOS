"""Versioned provider API schemas."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl, constr


class ProviderBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    kind: constr(strip_whitespace=True, min_length=1)
    base_url: HttpUrl
    models: List[str]
    api_key: Optional[str] = None


class ProviderCreate(ProviderBase):
    pass


class ProviderOut(ProviderBase):
    model_config = ConfigDict(from_attributes=True)

    enabled: bool = True
