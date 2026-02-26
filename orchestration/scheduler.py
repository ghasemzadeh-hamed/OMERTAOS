from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResourceRequest:
    cpu_millis: int
    memory_mb: int
    gpu: bool


@dataclass(frozen=True, slots=True)
class TaskSpec:
    task_id: str
    tenant_id: str
    request: ResourceRequest


class Scheduler:
    async def schedule(self, tasks: list[TaskSpec]) -> list[TaskSpec]:
        return sorted(tasks, key=lambda t: (not t.request.gpu, t.request.cpu_millis, t.request.memory_mb))
