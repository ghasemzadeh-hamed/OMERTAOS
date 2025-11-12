from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class InteractionCreate(BaseModel):
    agent_id: str
    user_id: Optional[str] = None
    model_version: str
    input_text: str
    output_text: str
    channel: Optional[str] = None


class SelfEditCreate(BaseModel):
    interaction_id: int
    original_output: str
    edited_output: str
    reason: Optional[str] = None
    reward: float


class SelfEditOut(BaseModel):
    id: int
    interaction_id: int
    original_output: str
    edited_output: str
    reason: Optional[str]
    reward: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InteractionOut(BaseModel):
    id: int
    agent_id: str
    user_id: Optional[str]
    model_version: str
    input_text: str
    output_text: str
    channel: Optional[str]
    created_at: datetime
    self_edits: List[SelfEditOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
