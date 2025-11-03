import asyncio

from app.main import health, healthz


def test_health_endpoint():
    result = asyncio.run(healthz())
    assert result["status"] == "ok"


def test_health_alias():
    result = asyncio.run(health())
    assert result["status"] == "ok"
    assert result["service"] == "control"
