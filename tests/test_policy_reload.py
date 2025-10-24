from pathlib import Path

from fastapi.testclient import TestClient

from control.app import app


def test_policy_reload_endpoint(tmp_path, monkeypatch):
    registry = tmp_path / "registry.yaml"
    registry.write_text("- version: 202403010000\n  artifact: bigdata/models/policy.sample.json\n", encoding="utf-8")
    monkeypatch.setattr("control.app.REGISTRY_PATH", registry)

    client = TestClient(app)
    response = client.post("/router/policy/reload", json={"version": "202403010000"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
