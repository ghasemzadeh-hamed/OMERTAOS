# S3.4 migration — Schemas and Protobuf consolidation

Date: 2026-07-12

Status: authored sources are canonical under `schemas/v1/`; generated Python
bindings are canonical under `shared/generated/python/`. Legacy copies remain
read-only compatibility inputs until S5.

## Impact analysis

- Canonical schema owner: `schemas/v1/`
- Canonical generated owner: `shared/generated/`
- Consumers changed: Gateway proto loader, Runtime Cargo build, Docker/Compose
  proto mounts and Python compatibility imports.
- Database, UI, auth and permission impact: none.
- Public HTTP impact: none. Internal gRPC wire messages/method names are retained.
- Risk: high because cross-language service contracts and builds are affected.

## Source consolidation

Canonical authored Protobuf sources are now:

```text
schemas/v1/protos/aion/v1/tasks.proto
schemas/v1/protos/runtime.proto
```

The Runtime source is content-equivalent to the two matching legacy copies;
platform line endings are normalized by Git/text comparisons.
Gateway resolves the canonical task source through `AION_PROTO_ROOT` or safe
known roots; local source/build and container `/protos` layouts are supported.
Runtime `build.rs` and its Docker image consume the canonical Runtime source.

Ten non-versioned JSON Schema files are content-identical with their `schemas/v1/`
counterparts and have no active non-versioned consumer. They remain compatibility
copies guarded by exact equality tests.

## Generated Python recovery

The previous files under schema source trees were wrappers to the removed
`os.control` namespace, not generated code. Message and gRPC bindings were
recovered from Git commit `7140004f` into:

```text
shared/generated/python/aion/v1/
```

The task wire schema and RPC method set match the current source, and round-trip
serialization is tested. The recovered descriptor contains historical language
option metadata from its generation commit. `grpc_tools` and system `protoc` are
not installed on this workstation, so fresh reproducible regeneration remains a
required follow-up before release acceptance. No generated output is represented
as freshly regenerated.

Legacy Python locations now re-export the canonical generated package. They and
the root `protos` symlink are retained for recovery/S5 review, but active build
and deployment references no longer depend on them.

## Validation

```powershell
python -m pytest tests/architecture/test_schema_consolidation.py -q
python -m pytest tests/architecture tests/control -q
npm run build --prefix gateway
cargo fmt --all --manifest-path runtime-daemon/Cargo.toml -- --check
cargo metadata --manifest-path runtime-daemon/Cargo.toml --no-deps --format-version 1
docker compose -f docker-compose.yml config --quiet
docker compose -f docker-compose.quickstart.yml config --quiet
```

Runtime Cargo compile/test remains blocked by crates.io access from Gate S2.
Fresh protobuf regeneration is also blocked by the unavailable compiler toolchain.
These limitations prevent production contract acceptance but do not invalidate
the source ownership migration.

## Migration and rollback

No database migration is required. Revert the S3.4 commit as one unit to restore
prior loader/build paths. Do not delete legacy proto/schema copies or generated
bindings; permanent retirement remains S5 and requires cross-language generation,
compatibility tests, Native/Quickstart acceptance and explicit human approval.
