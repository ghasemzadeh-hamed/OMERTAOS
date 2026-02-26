from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_target_architecture_contract_modules_exist() -> None:
    expected = [
        REPO_ROOT / "kernel" / "router" / "ai_router.py",
        REPO_ROOT / "data" / "rag" / "pipeline.py",
        REPO_ROOT / "data" / "vector" / "qdrant_client.py",
        REPO_ROOT / "shared" / "contracts" / "rag_contract.py",
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in expected if not path.exists()]
    assert not missing, f"missing target architecture modules: {missing}"
