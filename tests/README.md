# OMERTAOS verification strategy

This directory contains cross-component tests and architecture contracts.
Service-local unit tests remain colocated with their implementations.

**Document role:** current test map plus desired evidence. A test category in
this document is not proof that complete coverage exists.

## Current repository evidence

| Area | Current scope |
|---|---|
| Architecture | Canonical roots, ownership, forbidden imports, service boundaries, migration completion, and selected deployment contracts |
| Python/Control/Data | Targeted unit and integration-style tests under `tests/` and component trees |
| Gateway | TypeScript build plus repository test runner |
| Console | Vitest configuration and Playwright scenario sources |
| Runtime | Rust unit/migration tests, including fail-closed sandbox stubs |
| Deployment | Compose rendering, Docker builds, CAPO/static contracts, and acceptance scripts |

The exact executed scope depends on the command and commit. Report pass, fail,
skip, and blocked results separately.

## Architecture checks

```bash
python -m pytest tests/architecture -q
```

These tests protect the canonical request path and directory ownership. They do
not start a full stack and do not prove Runtime isolation or production network
policy.

## Component checks

```bash
# Gateway
npm run build --prefix gateway
npm test --prefix gateway

# Console
pnpm --dir console test -- --config vitest.config.mts
pnpm --dir console build

# Runtime
cargo fmt --check --manifest-path runtime-daemon/Cargo.toml
cargo test --manifest-path runtime-daemon/Cargo.toml --all-targets
```

Runtime migration tests currently verify that unavailable isolation backends
deny execution. Successful namespace, mount, seccomp, and process isolation
requires future host-level positive and escape tests.

## Current CI workflow

At the time of this document revision, `.github/workflows/ci.yml` defines:

1. architecture-contract tests;
2. Python lint and Rust Clippy;
3. Python/architecture and Rust tests;
4. an integration job that runs `tests/integration` when present;
5. Bandit, Cargo Audit, and Trivy jobs;
6. multi-architecture container builds;
7. SPDX SBOM generation.

This list describes workflow configuration, not a guaranteed successful run.
Review the GitHub Actions result for the exact commit and inspect skipped or
failed jobs.

## Evidence quality requirements

Security- and research-relevant tests should:

- include negative paths and tenant-boundary cases;
- use deterministic fixtures and record random seeds;
- avoid external network dependencies where practical;
- redact secrets and personal data from logs;
- preserve failure artifacts without converting flaky retries into success;
- state host/kernel requirements;
- report coverage only when the coverage command actually ran.

Future end-to-end and benchmark work should publish workload definitions,
environment manifests, raw observations, and analysis code. See the
[reproducibility protocol](../docs/research/reproducibility.md).
