from __future__ import annotations

from fastapi.testclient import TestClient

from control.app.main import app


def test_models_api_reads_canonical_registry_without_secret_values() -> None:
    response = TestClient(app).get("/models")

    assert response.status_code == 200
    models = response.json()
    assert models
    assert all(model["id"] and model["name"] and model["provider"] for model in models)
    assert all("api_key" not in model for model in models)


def test_versioned_models_alias_matches_internal_route() -> None:
    client = TestClient(app)
    assert client.get("/v1/models").json() == client.get("/models").json()
