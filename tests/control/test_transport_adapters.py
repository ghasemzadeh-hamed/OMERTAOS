from __future__ import annotations

from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from control.app.main import app
from control.transports import GrpcAdapter, GrpcTransportUnavailable
from control.transports.tasks_grpc import AionTasksGenericHandler, TaskId, TaskRequest


@dataclass(frozen=True)
class _MetadataItem:
    key: str
    value: str


class _FakeContext:
    def invocation_metadata(self) -> list[_MetadataItem]:
        return [_MetadataItem("tenant-id", "tenant-a"), _MetadataItem("x-request-id", "req-a")]

    def abort(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("abort should not be called for unary task adapters")


def test_all_control_health_aliases_share_canonical_payload() -> None:
    client = TestClient(app)
    expected = {"status": "ok", "service": "control"}

    for path in ("/health", "/healthz", "/v1/health", "/v1/healthz"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json() == expected


@pytest.mark.asyncio
async def test_grpc_adapter_fails_closed_without_server_factory() -> None:
    with pytest.raises(GrpcTransportUnavailable, match="no-op adapter"):
        await GrpcAdapter("0.0.0.0:50051").serve()


@pytest.mark.asyncio
async def test_grpc_adapter_delegates_to_server_factory() -> None:
    endpoints: list[str] = []

    async def serve(endpoint: str) -> None:
        endpoints.append(endpoint)

    await GrpcAdapter("0.0.0.0:50051", server_factory=serve).serve()

    assert endpoints == ["0.0.0.0:50051"]


def test_minimal_control_grpc_submit_fails_closed_without_runtime_transport() -> None:
    request = TaskRequest()
    request.schema_version = "1.0"
    request.task_id = "task-a"
    request.intent = "capo.r4.health_probe"
    request.metadata["agent_id"] = "agent-a"

    response = AionTasksGenericHandler().submit(request, _FakeContext())

    assert response.task_id == "task-a"
    assert response.intent == "capo.r4.health_probe"
    assert response.status == "ERROR"
    assert response.engine.route == "runtime"
    assert response.engine.chosen_by == "control"
    assert response.error.code == "RUNTIME_TRANSPORT_UNAVAILABLE"
    assert "synthetic success" in response.error.message
    assert response.metadata["tenant_id"] == "tenant-a"
    assert response.metadata["request_id"] == "req-a"


def test_minimal_control_grpc_status_fails_closed_without_storage() -> None:
    request = TaskId()
    request.task_id = "task-a"

    response = AionTasksGenericHandler().status_by_id(request, _FakeContext())

    assert response.task_id == "task-a"
    assert response.status == "ERROR"
    assert response.error.code == "TASK_STATUS_UNAVAILABLE"
