from __future__ import annotations

import ast
import importlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_canonical_python_modules_do_not_import_removed_control_os() -> None:
    roots = [
        REPO_ROOT / "control" / "app",
        REPO_ROOT / "control" / "models",
        REPO_ROOT / "control" / "schemas",
        REPO_ROOT / "schemas" / "v1",
        REPO_ROOT / "data",
    ]
    violations: list[str] = []
    for root in roots:
        for path in root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                if any(name == "control.os" or name.startswith("control.os.") for name in names):
                    violations.append(str(path.relative_to(REPO_ROOT)))
    assert not violations, "canonical modules import removed control.os: " + ", ".join(sorted(violations))


def test_recovered_compatibility_imports_resolve() -> None:
    for module in [
        "schemas.v1.provider",
        "control.schemas.provider",
        "control.models.registry",
        "data.retention_mongo",
    ]:
        importlib.import_module(module)


def test_model_registry_reads_canonical_profiles() -> None:
    registry_module = importlib.import_module("control.models.registry")
    registry = registry_module.ModelRegistry(REPO_ROOT / "registry" / "models")
    models = registry.list_models()
    assert models
    assert all(model["id"] and model["name"] and model["provider"] for model in models)
    legacy = [model for model in models if model["schema_status"] == "legacy-unversioned"]
    assert legacy, "legacy profiles should remain visible until their metadata is migrated"


def test_retention_helper_validates_and_creates_ttl_index() -> None:
    retention = importlib.import_module("data.retention_mongo")

    class Collection:
        call = None

        def create_index(self, keys, **kwargs):
            self.call = (keys, kwargs)

    collection = Collection()
    retention.ensure_ttl(collection, 7)
    assert collection.call == (
        [("created_at", 1)],
        {"expireAfterSeconds": 604800, "name": "created_at_ttl", "background": True},
    )

    try:
        retention.ensure_ttl(collection, 0)
    except ValueError as exc:
        assert str(exc) == "retention days must be greater than zero"
    else:
        raise AssertionError("non-positive retention must be rejected")


def test_model_profiles_have_one_canonical_owner() -> None:
    assert not (REPO_ROOT / "models").exists()
    assert list((REPO_ROOT / "registry" / "models").rglob("*.yaml"))


def test_current_design_documents_are_linked_from_readme() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    for path in [
        "docs/migration/s6-architecture-validation.md",
        "docs/architecture/aion-canonical-design.md",
        "docs/migration/aion-capability-recovery.md",
        "docs/adr/0001-canonical-aion-ownership.md",
    ]:
        assert path in readme
