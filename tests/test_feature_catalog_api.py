import os

from fastapi.testclient import TestClient

from os.control.os.http import app

os.environ.setdefault("AION_DISABLE_WORKERS", "1")


def test_feature_catalog_exposes_domains_for_console_pages():
    with TestClient(app) as client:
        response = client.get('/api/feature-catalog')

    assert response.status_code == 200
    payload = response.json()
    assert payload['total_domains'] == 20
    assert payload['total_feature_groups'] >= 80
    assert any(domain['id'] == 'ui-ux' for domain in payload['domains'])
