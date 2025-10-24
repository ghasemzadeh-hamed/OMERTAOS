"""Heuristic-driven AI kernel policy engine."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Dict

import yaml

from ..models import (
    KernelCanary,
    KernelChange,
    KernelGuardrail,
    KernelProposal,
    KernelScope,
)


class KernelPolicyEngine:
    """Generates safe kernel proposals based on telemetry and policy limits."""

    def __init__(self, policy_path: Path) -> None:
        self.policy_path = policy_path
        self._policy = self._load_policy()

    def _load_policy(self) -> Dict[str, object]:
        if not self.policy_path.exists():
            return {
                "allow": ["sysctl", "cgroup"],
                "ttl_seconds": 900,
                "max_risk": 0.5,
                "default_canary_percent": 20,
                "kpi_guard": {"degrade_threshold_pct": 5},
            }
        return yaml.safe_load(self.policy_path.read_text())

    def reload(self) -> None:
        self._policy = self._load_policy()

    def build_proposal(self, metrics: Dict[str, float]) -> KernelProposal:
        action = "sysctl"
        if metrics.get("net_rx_bytes_per_s", 0.0) > metrics.get("net_tx_bytes_per_s", 0.0) * 1.3:
            keys = ["net.core.netdev_max_backlog"]
            to_value = "5000"
        elif metrics.get("cpu_usage_pct", 0.0) > 85.0:
            keys = ["kernel.sched_schedstats"]
            to_value = "0"
        else:
            keys = ["net.ipv4.tcp_congestion_control"]
            to_value = random.choice(["bbr", "cubic", "reno"])
        changes = [
            KernelChange(
                key=key,
                from_value=None,
                to_value=to_value,
            )
            for key in keys
        ]
        proposal = KernelProposal(
            scope=KernelScope(type=action, keys=keys, target="node"),
            changes=changes,
            ttl_seconds=int(self._policy.get("ttl_seconds", 900)),
            canary=KernelCanary(
                percent=int(self._policy.get("default_canary_percent", 30)),
                granularity="nic-queue",
            ),
            risk_score=min(
                float(metrics.get("cpu_usage_pct", 0.0)) / 100.0,
                float(self._policy.get("max_risk", 0.8)),
            ),
            expected_impact={
                "latency_p95_ms": -15.0,
                "net_retx_pct": -1.0,
            },
            kpi_guard=KernelGuardrail(
                degrade_threshold_pct=float(
                    self._policy.get("kpi_guard", {}).get("degrade_threshold_pct", 5)
                )
            ),
        )
        return proposal
