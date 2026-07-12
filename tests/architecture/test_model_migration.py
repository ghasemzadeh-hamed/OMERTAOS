from __future__ import annotations

import ast
from pathlib import Path

import pytest

from control.models.registry import ModelRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_legacy_model_profiles_match_canonical_registry() -> None:
    legacy_root = REPO_ROOT / "models"
    canonical_root = REPO_ROOT / "registry" / "models"
    legacy = {path.relative_to(legacy_root) for path in legacy_root.rglob("*.yaml")}
    canonical = {path.relative_to(canonical_root) for path in canonical_root.rglob("*.yaml")}

    assert legacy == canonical
    assert len(canonical) == 11
    for relative in canonical:
        assert (legacy_root / relative).read_bytes() == (canonical_root / relative).read_bytes()


def test_legacy_models_python_files_are_compatibility_only() -> None:
    violations: list[str] = []
    for path in (REPO_ROOT / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                violations.append(f"{path.name}: {node.name}")
    assert not violations, "legacy model implementation remains: " + ", ".join(violations)


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
        "docker-compose.yml": "/app/registry/models",
        "docker-compose.quickstart.yml": "/app/registry/models",
        "deploy/compose/docker-compose.local.yml": "/app/registry/models",
    }
    for path, canonical in expected.items():
        source = (REPO_ROOT / path).read_text(encoding="utf-8")
        assert canonical in source, f"{path} does not reference {canonical}"
