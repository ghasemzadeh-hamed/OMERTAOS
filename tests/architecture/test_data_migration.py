from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_legacy_data_roots_are_retired() -> None:
    assert not (REPO_ROOT / "database").exists()
    assert not (REPO_ROOT / "db").exists()


def test_canonical_data_interfaces_exist() -> None:
    required = (
        "data/interfaces/__init__.py",
        "data/interfaces/adapter.py",
        "data/interfaces/repository.py",
    )
    assert all((REPO_ROOT / path).is_file() for path in required)
