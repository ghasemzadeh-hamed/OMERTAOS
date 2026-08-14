# S3.1 migration — database and db to Data

Date: 2026-07-12

Status: canonical implementations and interfaces live under `data/`; legacy
roots are compatibility-only and remain protected until S5.

## Gate exception

Gate S2 remains unaccepted because Runtime Cargo dependencies could not be
downloaded. The operator explicitly instructed execution of the next stage on
2026-07-12. This instruction authorizes S3.1 only; it does not convert the failed
Runtime build into a passed Gate or authorize the remaining S3 stages.

## Impact analysis

- Canonical owner: `data/`
- Legacy inputs: `database/` and `db/`
- Database objects and data: unchanged; no connection, query, migration, seed,
  `DROP` or `TRUNCATE` operation was executed.
- API/UI/auth/permission impact: none.
- Risk: medium because persistence interfaces are shared architecture contracts;
  no active application import used the legacy roots at migration time.

## Migration result

Thirteen `database/` implementation files were byte-identical to existing files
under `data/adapters`, `data/rag` or `data/vector`. They now explicitly re-export
the canonical objects rather than maintaining duplicate code.

Unique contracts were preserved as follows:

| Legacy contract | Canonical destination |
|---|---|
| synchronous `database/base.py` protocol | `data/interfaces/adapter.py::DatabaseAdapter` |
| async `database/adapters/base.py` protocol | `data/interfaces/adapter.py::AsyncDatabaseAdapter` |
| `db/interface.py::Repository` | `data/interfaces/repository.py::Repository` |
| `db/interface.py::UnitOfWork` | `data/interfaces/repository.py::UnitOfWork` |
| `db/interface.py::DatabaseAdapter` health contract | `data/interfaces/repository.py::HealthcheckAdapter` |

The canonical RAG pipeline referenced a removed `shared.contracts.rag_contract`
module. Its `Document` and `RAGEngine` port now lives at
`data/interfaces/rag.py`; no second shared-contract subsystem was introduced.

The existing `database/__init__.py` lazy compatibility layer and Mongo retention
wrapper remain. Empty vendor adapter placeholders under `db/adapters/` contain
no implementation and are retained for S5 review.

## Validation

```powershell
python -m pytest tests/data -q
python -m pytest tests/control -q
python -m pytest tests/architecture -q
python -m ruff check data database db tests/data tests/architecture/test_data_migration.py
docker compose -f docker-compose.quickstart.yml config --quiet
```

The Structure completion test remains expected-red while protected legacy roots
exist. S3.1 requires no Cargo build and does not change the open S2 Runtime
blocker.

## Rollback

Revert the S3.1 commit as one unit. No database rollback is required because no
schema or data changed. Do not remove legacy roots, adapter placeholders,
configuration or persistent state; permanent retirement remains an S5 action
requiring explicit human approval.
