from __future__ import annotations

from typing import Dict

import pytest

from app.routes.kernel_proposals import (
    AdminActionRequest,
    ProposalRequest,
    apply_now,
    approve_proposal,
    list_proposals,
    reject_proposal,
    submit_proposal,
)
from kernel.runtime import get_runtime, reset_runtime


@pytest.fixture(autouse=True)
def reset_kernel_runtime_fixture():
    reset_runtime()
    yield
    reset_runtime()


def _proposal_payload(overrides: Dict[str, object] | None = None) -> Dict[str, object]:
    base: Dict[str, object] = {
        "proposal_id": "kp_123",
        "source": "kbrain",
        "scope": {"type": "sysctl", "keys": ["net.ipv4.tcp_congestion_control"], "target": "node"},
        "changes": [
            {
                "key": "net.ipv4.tcp_congestion_control",
                "from": "cubic",
                "to": "bbr",
            }
        ],
        "ttl_seconds": 900,
        "canary": {"percent": 30, "granularity": "nic-queue"},
        "risk_score": 0.18,
        "expected_impact": {"latency_p95_ms": -20.0, "net_retx_pct": -0.5},
        "kpi_guard": {"degrade_threshold_pct": 5},
        "audit": {"created_by": "system-kbrain"},
    }
    if overrides:
        base.update(overrides)
    return base


def test_submit_and_list_proposals() -> None:
    request = ProposalRequest(**_proposal_payload())
    data = submit_proposal(request)
    assert data["status"] == "PENDING"
    assert data["audit"]["trace_id"].startswith("trace-")

    proposals = list_proposals()
    assert len(proposals) == 1
    assert proposals[0]["proposal_id"] == "kp_123"


def test_approval_and_apply_flow() -> None:
    submit_proposal(ProposalRequest(**_proposal_payload()))

    approve = approve_proposal("kp_123", AdminActionRequest(actor="admin@example.com"))
    assert approve["status"] == "APPROVED"

    payload = apply_now("kp_123", AdminActionRequest(actor="admin@example.com"))
    assert payload["status"] == "APPLIED"
    assert payload["before_metrics"]["latency_p95_ms"] > payload["after_metrics"]["latency_p95_ms"]
    assert payload["canary_plan"]["percent"] == 30


def test_reject_requires_reason() -> None:
    submit_proposal(ProposalRequest(**_proposal_payload({"proposal_id": "kp_456"})))
    with pytest.raises(Exception):
        reject_proposal("kp_456", AdminActionRequest(actor="admin@example.com"))


def test_ttl_expiry_marks_proposal_expired() -> None:
    payload = _proposal_payload({"proposal_id": "kp_ttl", "ttl_seconds": 0})
    data = submit_proposal(ProposalRequest(**payload))
    assert data["status"] == "PENDING"
    runtime = get_runtime()
    proposal = runtime.lifecycle.get("kp_ttl")
    proposal.created_at = proposal.created_at.replace(year=proposal.created_at.year - 1)
    proposal.expires_at = proposal.created_at
    body = list_proposals(status="EXPIRED")
    assert body[0]["status"] == "EXPIRED"
