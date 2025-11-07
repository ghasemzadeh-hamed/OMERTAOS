import asyncio
import base64
import hashlib
import hmac
import os
import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from app.control.app.core.deps import get_state  # type: ignore  # noqa: E402
from app.control.app.core.state import ControlState  # type: ignore  # noqa: E402
from app.control.main import app  # type: ignore  # noqa: E402
from app.control.app.api import webhooks as webhooks_module  # type: ignore  # noqa: E402


@pytest.fixture()
def client():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    state = ControlState()

    def _state_override() -> ControlState:
        return state

    original_startup = list(app.router.on_startup)
    original_shutdown = list(app.router.on_shutdown)
    app.router.on_startup = []
    app.router.on_shutdown = []

    app.dependency_overrides[get_state] = _state_override
    try:
        with TestClient(app) as test_client:
            yield test_client, state, loop
    finally:
        app.dependency_overrides.pop(get_state, None)
        app.router.on_startup = original_startup
        app.router.on_shutdown = original_shutdown
        loop.close()
        asyncio.set_event_loop(None)


def _auth_headers(secret: str, body: bytes, timestamp: int | None = None) -> dict[str, str]:
    ts = str(timestamp or int(time.time()))
    signature = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return {
        "X-Signature": signature,
        "X-Timestamp": ts,
        "Content-Type": "application/json",
    }


def test_webhook_enqueues_valid_event(client):
    http_client, state, loop = client
    os.environ["AION_WEBHOOK_SECRET"] = "supersecret"
    body = b'{"event_id":"evt_1","event":"ping","payload":42}'
    headers = _auth_headers("supersecret", body)

    response = http_client.post("/api/webhooks/github", data=body, headers=headers)
    assert response.status_code == 200
    event = loop.run_until_complete(state.event_queue.get())
    assert event["event_id"] == "evt_1"
    assert event["event_type"] == "ping"
    assert event["source"] == "github"


def test_webhook_rejects_invalid_signature(client):
    http_client, _, _ = client
    os.environ["AION_WEBHOOK_SECRET"] = "supersecret"
    headers = {
        "X-Signature": "deadbeef",
        "X-Timestamp": str(int(time.time())),
        "Content-Type": "application/json",
    }
    response = http_client.post("/api/webhooks/github", data=b"{}", headers=headers)
    assert response.status_code == 401


def test_webhook_supports_form_payload(client):
    http_client, state, loop = client
    os.environ.pop("AION_WEBHOOK_SECRET", None)
    body = "event=billing&event_id=evt_form&amount=10".encode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Timestamp": str(int(time.time())),
    }
    response = http_client.post("/api/webhooks/custom-1", data=body, headers=headers)
    assert response.status_code == 200
    event = loop.run_until_complete(state.event_queue.get())
    assert event["payload"]["event"] == "billing"
    assert event["event_id"] == "evt_form"


def test_webhook_normalizes_xml(client):
    http_client, state, loop = client
    os.environ.pop("AION_WEBHOOK_SECRET", None)
    xml_payload = b"<note><id>123</id></note>"
    headers = {"Content-Type": "text/xml", "X-Timestamp": str(int(time.time()))}
    response = http_client.post("/api/webhooks/custom-xml", data=xml_payload, headers=headers)
    assert response.status_code == 200
    event = loop.run_until_complete(state.event_queue.get())
    encoded = base64.b64encode(xml_payload).decode("ascii")
    assert event["payload"] == encoded
    assert event["event_type"] == "unknown"
    assert isinstance(event["event_id"], str)
    assert len(event["event_id"]) == 64  # sha256 hex digest


def test_webhook_rejects_oversized_payload(client):
    http_client, _, _ = client
    original_limit = webhooks_module.MAX_BODY_BYTES
    webhooks_module.MAX_BODY_BYTES = 16
    try:
        response = http_client.post(
            "/api/webhooks/custom-1",
            data=b"x" * 32,
            headers={"Content-Type": "application/json", "X-Timestamp": str(int(time.time()))},
        )
    finally:
        webhooks_module.MAX_BODY_BYTES = original_limit
    assert response.status_code == 413


def test_webhook_detects_replay(client):
    http_client, state, loop = client
    os.environ.pop("AION_WEBHOOK_SECRET", None)
    body = b'{"event_id":"evt_replay","event":"pong"}'
    headers = {"Content-Type": "application/json", "X-Timestamp": str(int(time.time()))}
    first = http_client.post("/api/webhooks/custom-1", data=body, headers=headers)
    assert first.status_code == 200
    loop.run_until_complete(state.event_queue.get())
    second = http_client.post("/api/webhooks/custom-1", data=body, headers=headers)
    assert second.status_code == 409


def test_webhook_rejects_timestamp_skew(client):
    http_client, _, _ = client
    os.environ["AION_WEBHOOK_SECRET"] = "supersecret"
    body = b"{}"
    headers = _auth_headers("supersecret", body, timestamp=int(time.time()) - 10000)
    response = http_client.post("/api/webhooks/custom-1", data=body, headers=headers)
    assert response.status_code == 400
