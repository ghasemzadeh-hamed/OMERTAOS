from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from control.app.main import app


def admin_headers() -> dict[str, str]:
    return {
        "authorization": "Bearer test-admin-token",
        "x-aion-roles": "admin",
        "x-aion-user-id": "admin-test",
    }


def test_proxy_profile_crud_masks_secrets(monkeypatch):
    monkeypatch.setenv("AION_GATEWAY_ADMIN_TOKEN", "test-admin-token")
    monkeypatch.setenv("AION_CONTROL_DISABLE_SECRETS", "1")
    monkeypatch.setenv("AION_CONTROL_LOCAL_SECRET_KEY", "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=")
    name = f"test-http-{uuid4()}"

    with TestClient(app) as client:
        create = client.post(
            "/v1/network/proxies",
            headers=admin_headers(),
            json={
                "name": name,
                "type": "http",
                "scope": "ai_providers",
                "host": "proxy.local",
                "port": 8080,
                "enabled": True,
                "secrets": {"password": "do-not-return"},
            },
        )
        assert create.status_code == 201
        payload = create.json()
        assert payload["has_secrets"] is True
        assert "password" not in payload

        profile_id = payload["id"]
        read = client.get(f"/v1/network/proxies/{profile_id}", headers=admin_headers())
        assert read.status_code == 200
        assert read.json()["name"] == name
        assert "do-not-return" not in read.text

        update = client.put(
            f"/v1/network/proxies/{profile_id}",
            headers=admin_headers(),
            json={"port": 8081, "fallback_direct": True},
        )
        assert update.status_code == 200
        assert update.json()["port"] == 8081
        assert update.json()["fallback_direct"] is True

        delete = client.delete(f"/v1/network/proxies/{profile_id}", headers=admin_headers())
        assert delete.status_code == 204


def test_proxy_profile_mutations_are_admin_only(monkeypatch):
    monkeypatch.setenv("AION_GATEWAY_ADMIN_TOKEN", "test-admin-token")
    with TestClient(app) as client:
        response = client.post(
            "/v1/network/proxies",
            headers={"x-aion-roles": "user"},
            json={"name": "blocked", "type": "direct", "scope": "global"},
        )

    assert response.status_code == 403
