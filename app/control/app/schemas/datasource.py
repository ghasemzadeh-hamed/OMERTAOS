"""Pydantic models for datasource management."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, constr


class DataSourceBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    kind: constr(strip_whitespace=True, min_length=1)
    dsn: constr(strip_whitespace=True, min_length=1)
    readonly: Optional[bool] = None


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceOut(DataSourceBase):
    enabled: bool = True

    class Config:
        orm_mode = True
