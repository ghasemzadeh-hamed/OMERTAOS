# Gate S3 report — Supporting Layer Migration

Date: 2026-08-10

Branch: `CAPO`

Status: **passed — executable dependencies are clean; historical evidence is classified**

## Gate result

R2 replaces the old raw-literal search with an executable architecture
contract. A name in an ADR, migration report, recovery document or centralized
guard fixture is historical evidence; it is not treated as a runtime
dependency. The Gate now proves these independent properties:

| Contract | Evidence | Result |
|---|---|---|
| No retired top-level path is tracked | `git ls-files -z` checked against the centralized fixture | Passed |
| Canonical Python has no retired import | AST import inspection across canonical Python roots | Passed |
| Active source/deploy has no retired runtime path | Source-aware patterns across canonical and deployment roots | Passed |
| Console follows the canonical boundary | Direct Control/Runtime URL guard | Passed |
| Historical names do not define ownership | Explicit ADR/CAPO/migration evidence classification | Passed |

The centralized list is
`tests/architecture/fixtures/retired_roots.json`. Architecture tests and the
working-tree structure audit consume this contract instead of duplicating raw
constants. Current `.codex` guidance and doctor scripts now list canonical
owners only.

## Validation

| Area | Command / evidence | Local result |
|---|---|---|
| R2 contract | `python -m pytest tests/architecture/test_canonical_contract.py -q` | Passed |
| Architecture | `python -m pytest tests/architecture -q` | Passed |
| Python full suite | `python -m pytest -q` | 164 passed, 2 skipped |
| Structure | `python scripts/check_structure_consistency.py` | Passed |
| Gateway | test and TypeScript build | 2 files / 6 tests passed; build passed |
| Console | Vitest and production build | 6 files / 11 tests passed; build passed |
| Bridge | server test/build and UI build | 2 files / 3 tests passed; both builds passed |
| Runtime local | format, then locked Clippy/test/build | Format passed; Clippy blocked before code analysis because the Windows host lacks `link.exe` |
| Diff | `git diff --check` | Passed; line-ending warnings only |

The pushed R2 commit is additionally evaluated by GitHub Actions. CI is the
authoritative locked Runtime result for this Windows host limitation. Commit
`91921367cdfa600abb91710f7d699a183af800fa` is covered by CI run
[`31358631289`](https://github.com/Hamedghz/OMERTAOS/actions/runs/31358631289):
architecture, lint, service builds, Python/Rust tests, the locked Runtime release
build, integration and security jobs passed. Its emulated arm64 Console image
job did not terminate, so R3 moves arm64 image builds to GitHub's native arm64
runner before evaluating Gate R on the R3 commit.

## Security and limitations

- The canonical request path remains `Console -> Gateway -> Control -> Runtime Daemon`.
- No auth, permission, public API, schema, data or production topology changed.
- No root, file, table, column or record was deleted.
- Gate S3 proves Structure ownership; it does not prove Native runtime, Docker
  runtime, feature completeness, merge readiness or production deployment.

## Migration and rollback

No database or data migration is required. Revert the single R2 commit to
restore the previous search contract and documentation. Do not restore retired
roots as part of rollback; Git history and the external R1 backup remain the
recovery sources.
