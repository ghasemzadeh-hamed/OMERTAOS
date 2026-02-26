from __future__ import annotations

from dataclasses import dataclass

from control_plane.runtime_client import ExecutionContextPayload, RuntimeDaemonClient


@dataclass(frozen=True)
class CpuAllocation:
    tenant_id: str
    agent_id: str
    cpuset: str
    quota_us: int
    period_us: int
    nice: int


PROFILE_CPU = {
    "lite": {"quota_us": 50_000, "period_us": 100_000, "cpuset": "0", "nice": 10, "cpu_cores": 1},
    "professional": {"quota_us": 100_000, "period_us": 100_000, "cpuset": "0-1", "nice": 0, "cpu_cores": 2},
    "enterprise": {"quota_us": 200_000, "period_us": 100_000, "cpuset": "0-3", "nice": -5, "cpu_cores": 4},
}


class CpuManager:
    def __init__(self, runtime_client: RuntimeDaemonClient | None = None) -> None:
        self._runtime = runtime_client or RuntimeDaemonClient()

    def allocate(self, tenant_id: str, agent_id: str, profile: str) -> CpuAllocation:
        cfg = PROFILE_CPU.get(profile, PROFILE_CPU["lite"])
        alloc = CpuAllocation(tenant_id, agent_id, cfg["cpuset"], cfg["quota_us"], cfg["period_us"], cfg["nice"])
        ctx = ExecutionContextPayload(
            agent_id=agent_id,
            tenant_id=tenant_id,
            cpu_cores=cfg["cpu_cores"],
            memory_mb=256,
            gpu_enabled=False,
            capabilities=["resource.allocate"],
        )
        self._runtime.allocate_resources(ctx, profile)
        return alloc
