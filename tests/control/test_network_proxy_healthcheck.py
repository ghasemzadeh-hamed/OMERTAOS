from __future__ import annotations

import pytest

from control.app.network.healthcheck import test_profile as run_healthcheck
from control.app.network.models import ProxyProfile


class FakeResponse:
    status_code = 204


class FakeAsyncClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def get(self, url: str):
        self.url = url
        return FakeResponse()


@pytest.mark.asyncio
async def test_healthcheck_uses_mocked_outbound_request(monkeypatch):
    monkeypatch.setattr("control.app.network.healthcheck.httpx.AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(
        "control.app.network.healthcheck.socket.getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("93.184.216.34", 443))],
    )
    profile = ProxyProfile(
        name="mocked",
        type="http",
        scope="ai_providers",
        host="proxy.local",
        port=8080,
        enabled=True,
    )

    result = await run_healthcheck(profile, "https://example.test/health")

    assert result["ok"] is True
    assert result["status_code"] == 204
    assert result["routed_via"] == "http"


@pytest.mark.asyncio
async def test_healthcheck_rejects_private_target(monkeypatch):
    monkeypatch.setattr(
        "control.app.network.healthcheck.socket.getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("127.0.0.1", 80))],
    )
    profile = ProxyProfile(name="blocked", type="direct", scope="global", enabled=True)

    with pytest.raises(ValueError, match="public addresses"):
        await run_healthcheck(profile, "http://localhost/internal")
