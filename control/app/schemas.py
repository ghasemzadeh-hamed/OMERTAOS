from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Optional


class TokenPayload(BaseModel):
    sub: str
    email: str
    role: str


class UserCreate(BaseModel):
    email: str
    password: str
    role: str = 'user'


class UserRead(BaseModel):
    id: int
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    intent: str
    params: dict[str, Any]
    preferred_engine: Optional[str] = Field(default=None, pattern='^(local|api|hybrid)$')
    priority: int = Field(default=1, ge=1, le=5)
    meta: dict[str, Any] | None = None


class TaskRead(BaseModel):
    id: int
    external_id: str
    intent: str
    params: dict[str, Any]
    preferred_engine: str | None
    priority: int
    status: str
    result: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivityLogRead(BaseModel):
    id: int
    action: str
    payload: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class RouterDecision(BaseModel):
    decision: str
    reason: str


class RouterResponse(BaseModel):
    decision: RouterDecision
    output: dict[str, Any]
