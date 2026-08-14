from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from control.app.main import app
from control.transports import GrpcAdapter, GrpcTransportUnavailable


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
