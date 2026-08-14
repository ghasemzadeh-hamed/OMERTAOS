from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResourceRequest:
    cpu_millis: int
    memory_mb: int
    gpu: bool

    def __post_init__(self) -> None:
        if self.cpu_millis <= 0:
            raise ValueError("cpu_millis must be positive")
        if self.memory_mb <= 0:
            raise ValueError("memory_mb must be positive")


@dataclass(frozen=True, slots=True)
class TaskSpec:
    task_id: str
    tenant_id: str
    request: ResourceRequest

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("task_id is required")
        if not self.tenant_id.strip():
            raise ValueError("tenant_id is required")


class Scheduler:
    """Prototype deterministic ordering; durable scheduling remains future work."""

    async def schedule(self, tasks: list[TaskSpec]) -> list[TaskSpec]:
        task_ids = [task.task_id for task in tasks]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("duplicate task_id in scheduling batch")
        return sorted(
            tasks,
            key=lambda task: (
                not task.request.gpu,
                task.request.cpu_millis,
                task.request.memory_mb,
                task.task_id,
            ),
        )
