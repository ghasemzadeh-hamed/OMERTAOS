from __future__ import annotations

from pathlib import Path

from kernel.kapply.actuator import KernelActuator
from kernel.kmon.telemetry import TelemetryMonitor
from kernel.netd.dataplane import NetDataplane
from kernel.safekeeper.manager import ProposalFactory, ProposalLifecycleManager
from kernel.safekeeper.policy import KernelPolicyEnforcer


class KernelRuntime:
    def __init__(self, root_dir: Path | None = None) -> None:
        base_dir = root_dir or Path(__file__).resolve().parents[2]
        policy_path = base_dir / "policies" / "kernel" / "ai-kernel-policy.yaml"
        telemetry = TelemetryMonitor()
        actuator = KernelActuator()
        dataplane = NetDataplane()
        policy = KernelPolicyEnforcer(policy_path)
        lifecycle = ProposalLifecycleManager(telemetry, actuator, dataplane, policy)
        self.telemetry = telemetry
        self.actuator = actuator
        self.dataplane = dataplane
        self.policy = policy
        self.lifecycle = lifecycle
        self.proposals = ProposalFactory(lifecycle)


_runtime: KernelRuntime | None = None


def get_runtime() -> KernelRuntime:
    global _runtime
    if _runtime is None:
        _runtime = KernelRuntime()
    return _runtime


def reset_runtime() -> None:
    global _runtime
    _runtime = None


__all__ = ["KernelRuntime", "get_runtime", "reset_runtime"]
