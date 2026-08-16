from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class NodeStateOut(str, Enum):
    healthy = "healthy"
    degraded = "degraded"
    unreachable = "unreachable"
    draining = "draining"


class RuntimeNodeRegistrationIn(BaseModel):
    node_id: str = Field(min_length=1, max_length=120)
    endpoint: str = Field(min_length=1, max_length=255)
    capabilities: list[str] = Field(default_factory=list)
    total_cpu_millis: int = Field(default=1000, gt=0)
    total_memory_mb: int = Field(default=512, gt=0)
    available_cpu_millis: int | None = Field(default=None, ge=0)
    available_memory_mb: int | None = Field(default=None, ge=0)
    tenant_ids: list[str] = Field(default_factory=list)
    software_version: str = Field(default="unknown", max_length=80)
    contract_version: str = Field(default="runtime.v1", max_length=80)
    trust_zone: str = Field(default="local", max_length=80)
    labels: dict[str, str] = Field(default_factory=dict)


class RuntimeNodeHeartbeatIn(BaseModel):
    available_cpu_millis: int = Field(ge=0)
    available_memory_mb: int = Field(ge=0)
    active_leases: int = Field(default=0, ge=0)
    state: NodeStateOut = NodeStateOut.healthy
    capabilities: list[str] | None = None


class RuntimeNodeOut(BaseModel):
    node_id: str
    endpoint: str
    state: NodeStateOut
    software_version: str
    contract_version: str
    trust_zone: str
    capabilities: list[str]
    tenant_ids: list[str]
    labels: dict[str, str]
    total_cpu_millis: int
    total_memory_mb: int
    available_cpu_millis: int
    available_memory_mb: int
    active_leases: int
    drain_requested: bool
    last_heartbeat_at: datetime | None


class RuntimeNodeList(BaseModel):
    items: list[RuntimeNodeOut]


class SchedulingRequestIn(BaseModel):
    task_id: str = Field(min_length=1, max_length=120)
    attempt_id: str = Field(min_length=1, max_length=120)
    tenant_id: str = Field(min_length=1, max_length=120)
    required_capabilities: list[str] = Field(default_factory=list)
    cpu_millis: int = Field(default=100, gt=0)
    memory_mb: int = Field(default=128, gt=0)
    strategy: str = Field(default="round_robin", pattern="^(round_robin|least_loaded)$")
    idempotency_key: str | None = Field(default=None, max_length=255)
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=0, ge=0)


class SchedulingResultOut(BaseModel):
    task_id: str
    attempt_id: str
    tenant_id: str
    strategy: str
    decision: str
    selected_node_id: str | None
    reason: str
    eligible_nodes: list[str]
    rejected_nodes: dict[str, str]
    idempotent_replay: bool
