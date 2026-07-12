from __future__ import annotations

from importlib import import_module

import pytest

from data.adapters.mongo_adapter import MongoAdapter
from data.adapters.postgres_adapter import PostgresAdapter
from data.adapters.redis_adapter import RedisAdapter
from data.adapters.sqlite_adapter import SQLiteAdapter
from data.interfaces import HealthcheckAdapter, Repository, UnitOfWork
from data.rag.embedding import embed_text
from data.rag.ingest import chunk_text
from data.rag.pipeline import SimpleRAGPipeline
from data.rag.reranker import rerank_by_score
from data.rag.retriever import search_documents


def test_legacy_adapter_exports_are_canonical_types() -> None:
    LegacyMongoAdapter = import_module("database.mongo_adapter").MongoAdapter
    LegacyPostgresAdapter = import_module("database.postgres_adapter").PostgresAdapter
    LegacyRedisAdapter = import_module("database.redis_adapter").RedisAdapter
    LegacySQLiteAdapter = import_module("database.sqlite_adapter").SQLiteAdapter

    assert LegacyMongoAdapter is MongoAdapter
    assert LegacyPostgresAdapter is PostgresAdapter
    assert LegacyRedisAdapter is RedisAdapter
    assert LegacySQLiteAdapter is SQLiteAdapter


def test_legacy_rag_exports_are_canonical_objects() -> None:
    legacy_embed_text = import_module("database.embedding").embed_text
    legacy_chunk_text = import_module("database.ingest").chunk_text
    LegacyPipeline = import_module("database.pipeline").SimpleRAGPipeline
    legacy_rerank = import_module("database.reranker").rerank_by_score
    legacy_search = import_module("database.retriever").search_documents

    assert legacy_embed_text is embed_text
    assert legacy_chunk_text is chunk_text
    assert LegacyPipeline is SimpleRAGPipeline
    assert legacy_rerank is rerank_by_score
    assert legacy_search is search_documents


def test_db_interface_exports_canonical_abstract_contracts() -> None:
    legacy_interface = import_module("db.interface")

    assert legacy_interface.DatabaseAdapter is HealthcheckAdapter
    assert legacy_interface.Repository is Repository
    assert legacy_interface.UnitOfWork is UnitOfWork
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
