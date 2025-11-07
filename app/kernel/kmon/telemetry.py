from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict

from ..kbrain.proposal import KernelProposal


@dataclass
class TelemetrySnapshot:
    captured_at: datetime
    metrics: Dict[str, float]


class TelemetryMonitor:
    """Collects in-memory metrics snapshots for proposals."""

    def __init__(self) -> None:
        # Use deterministic baseline metrics for tests while allowing overrides later.
        self._baseline: Dict[str, float] = {
            "latency_p95_ms": 120.0,
            "net_retx_pct": 0.8,
            "throughput_gbps": 40.0,
        }

    def snapshot(self, proposal: KernelProposal) -> TelemetrySnapshot:
        # In a real system this would query eBPF/perf; here we return a stable baseline.
        return TelemetrySnapshot(captured_at=datetime.now(timezone.utc), metrics=dict(self._baseline))

    def project(self, proposal: KernelProposal, baseline: TelemetrySnapshot) -> TelemetrySnapshot:
        projected = dict(baseline.metrics)
        for key, delta in proposal.expected_impact.items():
            projected[key] = projected.get(key, 0.0) + delta
        return TelemetrySnapshot(captured_at=datetime.now(timezone.utc), metrics=projected)

    def set_baseline(self, metric: str, value: float) -> None:
        self._baseline[metric] = value
