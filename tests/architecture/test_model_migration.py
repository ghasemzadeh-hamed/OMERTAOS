from __future__ import annotations

from pathlib import Path

import pytest

from control.models.registry import ModelRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_legacy_model_root_is_retired_and_canonical_profiles_remain() -> None:
    canonical_root = REPO_ROOT / "registry" / "models"
    canonical = {path.relative_to(canonical_root) for path in canonical_root.rglob("*.yaml")}

    assert not (REPO_ROOT / "models").exists()
    assert len(canonical) == 11


def test_model_registry_rejects_embedded_secrets(tmp_path: Path) -> None:
    profile = tmp_path / "unsafe.yaml"
    profile.write_text(
        "name: unsafe\nprovider: example\nversion: 1\napi_key: plaintext-secret\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must reference secrets"):
        ModelRegistry(tmp_path)


def test_active_model_directory_configuration_is_canonical() -> None:
    expected = {
        ".env.example": "${APP_DIR}/registry/models",
        "dev.env": "/srv/app/registry/models",
        "deploy/docker/compose/quickstart.yml": "/app/registry/models",
        "deploy/docker/compose/local.yml": "/app/registry/models",
    }
    for path, canonical in expected.items():
        source = (REPO_ROOT / path).read_text(encoding="utf-8")
        assert canonical in source, f"{path} does not reference {canonical}"
