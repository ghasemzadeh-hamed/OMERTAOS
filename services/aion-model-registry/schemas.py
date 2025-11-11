from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ModelRegister(BaseModel):
    name: str
    parent: Optional[str] = None
    path: str
    score: float
    metadata: Dict[str, str] = Field(default_factory=dict)


class ModelOut(BaseModel):
    id: int
    name: str
    parent: Optional[str]
    path: str
    score: float
    active: bool
    metadata: Dict[str, str] = Field(alias="metadata_json")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RouteRule(BaseModel):
    agent_id: str
    model_name: str
