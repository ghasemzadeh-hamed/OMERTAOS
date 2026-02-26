from __future__ import annotations

from dataclasses import dataclass

from control_plane.runtime_client import ExecutionContextPayload, RuntimeDaemonClient


@dataclass(frozen=True)
class GpuAllocation:
    tenant_id: str
    agent_id: str
    enabled: bool
    devices: tuple[str, ...]
    fractional: float | None = None


class GpuManager:
    def __init__(self, runtime_client: RuntimeDaemonClient | None = None) -> None:
        self._runtime = runtime_client or RuntimeDaemonClient()

    def allocate(self, tenant_id: str, agent_id: str, profile: str, fractional: float | None = None) -> GpuAllocation:
        if profile == "lite":
            return GpuAllocation(tenant_id, agent_id, False, tuple())
        enabled = profile in {"professional", "enterprise"}
        devices = ("0",) if profile == "professional" else ("0", "1") if enabled else tuple()
        ctx = ExecutionContextPayload(
            agent_id=agent_id,
            tenant_id=tenant_id,
            cpu_cores=1,
            memory_mb=1024,
            gpu_enabled=enabled,
            capabilities=["resource.allocate"],
        )
        self._runtime.allocate_resources(ctx, profile)
        return GpuAllocation(tenant_id, agent_id, enabled, devices, fractional)
