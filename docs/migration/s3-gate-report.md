# Gate S3 report — Supporting Layer Migration

Date: 2026-07-15

Branch: `capo-structure`

Status: **not passed — implementation checks are green, literal legacy-path searches remain red**

## Gate result

S3.1 through S3.7 have canonical implementations, compatibility tests and
migration notes. The executable tests/builds passed, but the literal Gate S3
search contract did not reach zero:

| Check | Result |
|---|---|
| `control-plane` outside `docs/migration/` | 25 matches |
| `rust-runtime` outside `docs/migration/` | 26 matches |
| Python `from database` / `import database` | 0 matches |
| Python `from db` / `import db` | 0 matches |
| `schemas/protos`, `shared/proto`, `root/protos` | 0 matches |

> S6 correction (2026-07-15): the earlier literal search was a false negative.
> Byte-identical aliases still existed under `schemas/protos`, `schemas/proto`,
> `schemas/config`, `schemas/events`, root schema JSON files and `shared/proto`.
> S6 retired those aliases to migration evidence and changed the architecture
> test to require their absence.

Remaining service-root matches include protected compatibility manifests/source,
migration architecture tests, cleanup tooling and historical/current documents
outside `docs/migration/`. Examples include `rust-runtime/Cargo.toml`, Runtime
compatibility documentation, `tests/architecture/test_runtime_migration.py` and
`scripts/cleanup_repo.py`.

Removing or renaming those references in S3 would conceal protected migration
inputs and violate the no-deletion rule. Their retirement belongs to S5 after S4,
Native/Quickstart evidence and explicit human approval. Therefore Gate S3 is not
accepted even though active supporting-layer imports are canonical.

## Validation

| Area | Command / evidence | Result |
|---|---|---|
| Python | Architecture, Control and Data tests excluding the final Structure gate | 94 passed, 1 deselected, 2 existing deprecation warnings |
| Gateway | TypeScript build | Passed |
| Bridge Server | TypeScript build | Passed |
| Bridge Server | Vitest | 2 files / 3 tests passed |
| Bridge UI | Vite production build | Passed; 40 modules transformed |
| Compose | Root, Quickstart and Local configuration rendering | Passed |
| Runtime static | Cargo format and no-dependency metadata | Passed |
| Diff | `git diff --check` | Passed with expected Windows line-ending warnings |

The Bridge toolchain was repaired before this Gate. The unavailable
`@microsoft/ai-mcp-sdk` dependency was replaced with official stable v1
`@modelcontextprotocol/sdk`, Ajv validates tool inputs, the missing Vite React
plugin and UI `index.html` were added, and stdio logs were moved off stdout.
No lockfile existed before S3.7 and none was generated.

## Security and limitations

- Windows Bridge calls Gateway only; direct Control configuration/calls are gone.
- Tokens remain environment-only and are not included in manifests or logs.
- MCP input validation fails closed and execution errors return bounded messages.
- Agent Catalog endpoints remain unavailable and were not reconstructed.
- Windows/WSL/ODR runtime acceptance was not available on this host.
- Gate S2 remains separately blocked until Runtime Cargo test/build can resolve
  its registry dependencies.

## Migration and rollback

No database or data migration is required. Revert the S3.5-S3.7 commit to restore
the previous supporting-layer paths and Bridge dependency/configuration. Preserve
both Windows Bridge trees, legacy service roots, configuration and persistent
state. This report records a failed Gate and must not be used as approval for S4,
S5, merge or production deployment.
