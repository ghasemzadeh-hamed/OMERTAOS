from __future__ import annotations

from collections.abc import Iterator
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from control.app.network.migrate import apply_schema
from control.app.runtime_nodes.lifecycle import (
    RuntimeLifecycleConfig,
    RuntimeNodeLifecycle,
    probe_runtime,
)
from control.app.runtime_nodes import lifecycle as lifecycle_module
from control.scheduling.models import RuntimeNode


def _config(**overrides: str) -> RuntimeLifecycleConfig:
    values = {
        "AION_RUNTIME_AUTO_REGISTER": "true",
        "AION_RUNTIME_NODE_ID": "runtime-a",
        "AION_RUNTIME_ENDPOINT": "runtime:50051",
        "AION_RUNTIME_CAPABILITIES": "terminal.execute",
        "AION_RUNTIME_TENANT_IDS": "tenant-a,tenant-b",
        "AION_RUNTIME_TOTAL_CPU_MILLIS": "1000",
        "AION_RUNTIME_TOTAL_MEMORY_MB": "512",
        "AION_RUNTIME_HEARTBEAT_INTERVAL_SECONDS": "10",
        "AION_RUNTIME_PROBE_TIMEOUT_SECONDS": "3",
        **overrides,
    }
    return RuntimeLifecycleConfig.from_env(values)


@pytest.fixture
def session_factory() -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    apply_schema(engine)
    yield sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    engine.dispose()


def test_runtime_lifecycle_config_is_opt_in_and_bounded() -> None:
    assert RuntimeLifecycleConfig.from_env({}).enabled is False
    assert _config().tenant_ids == ("tenant-a", "tenant-b")

    with pytest.raises(ValueError, match="must not exceed 20"):
        _config(AION_RUNTIME_HEARTBEAT_INTERVAL_SECONDS="21")
    with pytest.raises(ValueError, match="must not exceed the heartbeat interval"):
        _config(AION_RUNTIME_PROBE_TIMEOUT_SECONDS="11")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ('{"status":"ready"}', True),
        ("not-json", False),
    ],
)
async def test_runtime_probe_requires_ready_json_and_closes_channel(
    monkeypatch: pytest.MonkeyPatch,
    payload: str,
    expected: bool,
) -> None:
    class FakeChannel:
        closed = False

        async def close(self) -> None:
            self.closed = True

    class QueryMetrics:
        async def __call__(self, request: object, *, timeout: float) -> object:
            assert getattr(request, "tenant_id") == "system"
            assert timeout == 2.0
            return SimpleNamespace(ok=True, json=payload)

    channel = FakeChannel()
    monkeypatch.setattr(
        lifecycle_module.grpc.aio,
        "insecure_channel",
        lambda endpoint: channel,
    )
    monkeypatch.setattr(
        lifecycle_module.runtime_pb2_grpc,
        "RuntimeServiceStub",
        lambda _channel: SimpleNamespace(QueryMetrics=QueryMetrics()),
    )

    assert await probe_runtime("runtime:50051", 2.0) is expected
    assert channel.closed is True


@pytest.mark.asyncio
async def test_reachable_runtime_is_registered_and_heartbeated(
    session_factory: sessionmaker[Session],
) -> None:
    calls: list[tuple[str, float]] = []

    async def reachable(endpoint: str, timeout: float) -> bool:
        calls.append((endpoint, timeout))
        return True

    lifecycle = RuntimeNodeLifecycle(
        _config(),
        session_factory=session_factory,
        probe=reachable,
        schema_initializer=lambda: None,
    )

    assert await lifecycle.sync_once() is True
    with session_factory() as db:
        node = db.get(RuntimeNode, "runtime-a")
        assert node is not None
        assert node.endpoint == "runtime:50051"
        assert node.state == "healthy"
        assert node.tenant_ids_json == '["tenant-a","tenant-b"]'
        assert node.capabilities_json == '["terminal.execute"]'
        assert node.last_heartbeat_at is not None
    assert calls == [("runtime:50051", 3.0)]


@pytest.mark.asyncio
async def test_unreachable_runtime_is_not_registered(
    session_factory: sessionmaker[Session],
) -> None:
    async def unreachable(_endpoint: str, _timeout: float) -> bool:
        return False

    lifecycle = RuntimeNodeLifecycle(
        _config(),
        session_factory=session_factory,
        probe=unreachable,
        schema_initializer=lambda: None,
    )

    assert await lifecycle.sync_once() is False
    with session_factory() as db:
        assert db.get(RuntimeNode, "runtime-a") is None


@pytest.mark.asyncio
async def test_lifecycle_preserves_operator_drain(
    session_factory: sessionmaker[Session],
) -> None:
    async def reachable(_endpoint: str, _timeout: float) -> bool:
        return True

    lifecycle = RuntimeNodeLifecycle(
        _config(),
        session_factory=session_factory,
        probe=reachable,
        schema_initializer=lambda: None,
    )
    assert await lifecycle.sync_once() is True
    with session_factory() as db:
        node = db.get(RuntimeNode, "runtime-a")
        assert node is not None
        node.drain_requested = True
        node.state = "draining"
        db.commit()

    assert await lifecycle.sync_once() is True
    with session_factory() as db:
        node = db.get(RuntimeNode, "runtime-a")
        assert node is not None
        assert node.drain_requested is True
        assert node.state == "draining"
