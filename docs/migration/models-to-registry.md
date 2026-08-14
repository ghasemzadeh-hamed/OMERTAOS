# S3.2 migration — models to Registry

Date: 2026-07-12

Status: Registry owns model metadata; root `models/` is compatibility-only and
remains protected until S5.

## Impact analysis

- Canonical metadata owner: `registry/models/`
- Canonical reader/router owner: `control/models/`
- Canonical provider transport owner: `integrations/providers/`
- Legacy input: root `models/`
- Database and public API impact: none; existing `/models` and `/v1/models`
  responses remain backed by the canonical Registry reader.
- Security impact: embedded profile secrets and provider redirects fail closed.
- Risk: medium because model routing metadata and provider credentials are
  sensitive shared contracts.

## Migration result

All 11 YAML profiles under root `models/` are byte-identical to their
`registry/models/` counterparts. The canonical tree remains the writable source;
the root mirror is guarded by an equality test and receives no new behavior.

Python ownership was split by responsibility:

| Legacy file | Canonical destination |
|---|---|
| `models/registry.py` | explicit compatibility exports from `control/models/registry.py` |
| model selection/client facade in `models/client.py` | `control/clients/models/client.py` |
| HTTP provider call | `integrations/providers/http_llm.py` |

The HTTP provider requires an absolute HTTP(S) endpoint, positive timeout/token
limit, disables redirects and validates the response shape. Local providers do
not receive API credentials. Registry profiles may contain credential references
but are rejected when plaintext keys such as `api_key`, password or token are
embedded.

Active Control metadata paths in `.env.example`, `dev.env` and root Compose now
point to `registry/models`. Paths such as `/data/models/kimi-k2` are model-weight
mounts, not Registry metadata, and were intentionally unchanged.

## Validation

```powershell
python -m pytest tests/control/test_model_client.py tests/control/test_model_registry_api.py -q
python -m pytest tests/architecture/test_model_migration.py -q
python -m pytest tests/control tests/architecture -q
python -m ruff check control/clients/models integrations/providers models tests/control/test_model_client.py tests/architecture/test_model_migration.py
docker compose -f docker-compose.yml config --quiet
docker compose -f docker-compose.quickstart.yml config --quiet
```

No network provider request is made by tests; HTTP calls are mocked. Gate S2
remains open because Runtime Cargo build is blocked, and the Structure completion
gate remains expected-red while protected roots exist.

## Migration and rollback

No database migration is required. Revert the S3.2 commit as one unit to restore
the previous client/config paths. Do not delete the root mirror or credentials;
permanent retirement remains an S5 action requiring explicit human review.
