import asyncio

from app.main import healthz


def test_health_endpoint():
    result = asyncio.run(healthz())
    assert result["status"] == "ok"
