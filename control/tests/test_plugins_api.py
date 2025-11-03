"""Tests for the plugin registry FastAPI endpoints."""
from fastapi.testclient import TestClient

from aionos_control.main import app

client = TestClient(app)


def test_list_plugins_contains_entries():
    response = client.get("/plugins/")
    assert response.status_code == 200
    payload = response.json()
    assert "available" in payload
    available = set(payload["available"])
    assert {"cleanlab", "stumpy", "nevergrad"}.issubset(available)


def test_call_plugin_requires_valid_name():
    response = client.post("/plugins/call", json={"name": "   "})
    assert response.status_code == 400


def test_calling_unknown_plugin_returns_404():
    response = client.post("/plugins/call", json={"name": "unknown"})
    assert response.status_code == 404


def test_calling_plugin_without_extra_returns_hint():
    payload = {
        "name": "cleanlab",
        "params": {"y_true": [0, 1], "y_pred_proba": [[0.9, 0.1], [0.2, 0.8]]},
    }
    response = client.post("/plugins/call", json=payload)
    assert response.status_code == 424
    assert "Install extras" in response.json()["detail"]
