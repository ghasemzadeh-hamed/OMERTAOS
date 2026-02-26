from __future__ import annotations

from dataclasses import dataclass

from control_plane.runtime_client import ExecutionContextPayload, RuntimeDaemonClient


@dataclass(frozen=True)
class MemoryAllocation:
    tenant_id: str
    agent_id: str
    memory_max: int
    memory_swap_max: int
    oom_score_adj: int


PROFILE_MEMORY = {
    "lite": {"memory_max": 512 * 1024 * 1024, "memory_swap_max": 0, "oom_score_adj": 500, "memory_mb": 512},
    "professional": {"memory_max": 2 * 1024 * 1024 * 1024, "memory_swap_max": 512 * 1024 * 1024, "oom_score_adj": 250, "memory_mb": 2048},
    "enterprise": {"memory_max": 8 * 1024 * 1024 * 1024, "memory_swap_max": 2 * 1024 * 1024 * 1024, "oom_score_adj": 100, "memory_mb": 8192},
}


class MemoryManager:
    def __init__(self, runtime_client: RuntimeDaemonClient | None = None) -> None:
        self._runtime = runtime_client or RuntimeDaemonClient()

    def allocate(self, tenant_id: str, agent_id: str, profile: str) -> MemoryAllocation:
        cfg = PROFILE_MEMORY.get(profile, PROFILE_MEMORY["lite"])
        alloc = MemoryAllocation(tenant_id, agent_id, cfg["memory_max"], cfg["memory_swap_max"], cfg["oom_score_adj"])
        ctx = ExecutionContextPayload(
            agent_id=agent_id,
            tenant_id=tenant_id,
            cpu_cores=1,
            memory_mb=cfg["memory_mb"],
            gpu_enabled=False,
            capabilities=["resource.allocate"],
        )
        self._runtime.allocate_resources(ctx, profile)
        return alloc
