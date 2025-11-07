from __future__ import annotations

import base64
from importlib import reload
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from os import config as config_module


@pytest.fixture()
def client(tmp_path, monkeypatch):
    storage_dir = tmp_path / "memory"
    monkeypatch.setenv("AION_CONTROL_MEMORY_STORAGE_PATH", str(storage_dir))
    reload(config_module)
    config_module.get_settings.cache_clear()
    from os import main as main_module

    reload(main_module)
    return TestClient(main_module.app)


def test_memory_ingest_and_status(client: TestClient):
    data = base64.b64encode(b"hello world").decode()
    payload = {
        "profile": "shortform",
        "total_chunks": 1,
        "chunk_index": 0,
        "chunk_data": data,
    }

    response = client.post("/v1/memory/ingest", json=payload)
    assert response.status_code == 200
    upload = response.json()
    assert upload["state"] in {"receiving", "ready"}
    upload_id = upload["upload_id"]

    status = client.get("/v1/memory/status", params={"upload_id": upload_id})
    assert status.status_code == 200
    body = status.json()
    assert body["uploads"][0]["upload_id"] == upload_id
    assert body["uploads"][0]["bytes_received"] > 0


def test_define_profile_persists(client: TestClient, tmp_path: Path):
    profile_payload = {
        "name": "code",
        "embedding_model": "text-embedding-3-small",
        "chunk_size": 1024,
        "pipeline": ["chunk", "embed", "store"],
        "retention_days": 45,
    }
    result = client.post("/v1/memory/profile", json=profile_payload)
    assert result.status_code == 200
    body = result.json()
    assert body["name"] == "code"

    status = client.get("/v1/memory/status")
    assert status.status_code == 200
    profiles = status.json()["profiles"]
    assert any(item["name"] == "code" for item in profiles)
