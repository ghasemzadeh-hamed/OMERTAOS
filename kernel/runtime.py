from __future__ import annotations

from pathlib import Path

from .kapply.actuator import KernelActuator
from .kmon.telemetry import TelemetryMonitor
from .netd.dataplane import NetDataplane
from .safekeeper.manager import ProposalFactory, ProposalLifecycleManager
from .safekeeper.policy import KernelPolicyEnforcer


class KernelRuntime:
    def __init__(self, root_dir: Path | None = None) -> None:
        base_dir = root_dir or Path(__file__).resolve().parents[1]
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
