from __future__ import annotations

import asyncio

import pytest

from control.clients.runtime import (
    RuntimeDaemonClient,
    RuntimeEnvelope,
    RuntimeTransportUnavailable,
)


class RecordingTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, RuntimeEnvelope, float]] = []

    async def execute(
        self,
        endpoint: str,
        envelope: RuntimeEnvelope,
        *,
        timeout_seconds: float,
    ) -> dict[str, object]:
        self.calls.append((endpoint, envelope, timeout_seconds))
        return {"ok": True, "agent_id": envelope.agent_id}


class SlowTransport:
    async def execute(
        self,
        endpoint: str,
        envelope: RuntimeEnvelope,
        *,
        timeout_seconds: float,
    ) -> dict[str, object]:
        await asyncio.sleep(timeout_seconds * 10)
        return {"ok": True}


def test_runtime_envelope_requires_identity_and_command() -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        RuntimeEnvelope(tenant_id="", agent_id="agent-1", argv=("echo",))
    with pytest.raises(ValueError, match="agent_id"):
        RuntimeEnvelope(tenant_id="tenant-1", agent_id="", argv=("echo",))
    with pytest.raises(ValueError, match="argv"):
        RuntimeEnvelope(tenant_id="tenant-1", agent_id="agent-1", argv=())


@pytest.mark.asyncio
async def test_runtime_client_fails_closed_without_transport() -> None:
    client = RuntimeDaemonClient(endpoint="runtime:50051")
    envelope = RuntimeEnvelope("tenant-1", "agent-1", ("echo", "ok"))

    with pytest.raises(RuntimeTransportUnavailable, match="synthetic success"):
        await client.execute(envelope)


@pytest.mark.asyncio
async def test_runtime_client_delegates_to_bounded_transport() -> None:
    transport = RecordingTransport()
    client = RuntimeDaemonClient(
        endpoint="runtime:50051",
        transport=transport,
        timeout_seconds=0.5,
    )
    envelope = RuntimeEnvelope("tenant-1", "agent-1", ("echo", "ok"))

    assert await client.execute(envelope) == {"ok": True, "agent_id": "agent-1"}
    assert transport.calls == [("runtime:50051", envelope, 0.5)]


@pytest.mark.asyncio
async def test_runtime_client_enforces_timeout() -> None:
    client = RuntimeDaemonClient(
        endpoint="runtime:50051",
        transport=SlowTransport(),
        timeout_seconds=0.01,
    )

    with pytest.raises(TimeoutError):
        await client.execute(RuntimeEnvelope("tenant-1", "agent-1", ("sleep",)))
