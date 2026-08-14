"""Versioned datasource API schemas."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, constr


class DataSourceBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    kind: constr(strip_whitespace=True, min_length=1)
    dsn: constr(strip_whitespace=True, min_length=1)
    readonly: Optional[bool] = None


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceOut(DataSourceBase):
    model_config = ConfigDict(from_attributes=True)

    enabled: bool = True
