import os
from pathlib import Path

from fastapi.testclient import TestClient

from os.control.os.http import app
from os.control.os.recommendations import FEATURE_LATENTBOX, load_latentbox_catalog

os.environ.setdefault("AION_DISABLE_WORKERS", "1")


def test_latentbox_loader_reads_catalog():
    records = load_latentbox_catalog(Path("config/latentbox"))
    ids = {record.id for record in records}
    assert "latentbox:ai:llm:chatgpt" in ids
    assert any(record.category == "image" for record in records)


def test_recommendations_endpoint_returns_tools():
    if not FEATURE_LATENTBOX:
        return
    headers = {"x-aion-roles": "ROLE_ADMIN"}
    with TestClient(app) as client:
        response = client.get("/api/v1/recommendations/tools", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["tools"], "should return latentbox tools"

        response = client.get(
            "/api/v1/recommendations/tools",
            headers=headers,
            params={"scenario": "gen_art", "capabilities": ["image"]},
        )
        assert response.status_code == 200
        ranked = response.json()["tools"]
        assert any(tool["category"] == "image" for tool in ranked)

        sync_response = client.post("/api/v1/recommendations/tools/sync", headers=headers)
        assert sync_response.status_code == 200
        synced = sync_response.json()
        assert synced["synced"] >= 0
