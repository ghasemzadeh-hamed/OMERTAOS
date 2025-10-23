from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TaskCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(alias='task_id')
    intent: str
    params: dict
    preferred_engine: Optional[str] = Field(default=None, alias='preferred_engine')
    priority: Optional[str] = None
    meta: Optional[dict] = None


class TaskRouteDecision(BaseModel):
    decision: str
    reason: str


class TaskDispatchResponse(BaseModel):
    task_id: str
    decision: str
    status: str
    reason: str


class TaskDTO(BaseModel):
    id: int
    project_id: int
    title: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
