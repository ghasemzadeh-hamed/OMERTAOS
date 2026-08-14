from __future__ import annotations

from importlib import import_module

import pytest

from data.interfaces import HealthcheckAdapter, Repository, UnitOfWork
from data.rag.embedding import embed_text
from data.rag.ingest import chunk_text
from data.rag.reranker import rerank_by_score


def test_legacy_data_modules_are_retired() -> None:
    for module in ("database.mongo_adapter", "database.embedding", "db.interface"):
        with pytest.raises(ModuleNotFoundError):
            import_module(module)


def test_canonical_abstract_contracts_remain_abstract() -> None:
    with pytest.raises(TypeError):
        Repository()
    with pytest.raises(TypeError):
        UnitOfWork()
    with pytest.raises(TypeError):
        HealthcheckAdapter()


def test_canonical_rag_helpers_preserve_deterministic_behavior() -> None:
    assert chunk_text("one two three", chunk_size=2, overlap=1) == ["one two", "two three", "three"]
    assert embed_text("stable", dims=8) == embed_text("stable", dims=8)
    assert len(embed_text("stable", dims=8)) == 8
    assert [item["id"] for item in rerank_by_score([{"id": "low", "score": 0.1}, {"id": "high", "score": 0.9}])] == ["high", "low"]
