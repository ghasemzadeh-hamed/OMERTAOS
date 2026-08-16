# CAPO R4 local validation report

Date: 2026-08-16

Branch: `codex/capo-r4-validation`

Canonical CAPO commit identified from GitHub API: `863e00c6398bdd03a78140e9607c032a8b1025d3`

Local checkpoint commit: `c1d5827cad23e7db55a29d1d60c0ced9ad17bac0`

Note: this workspace was reconstructed from the CAPO source archive because
history-preserving Git network operations timed out locally. Local Git commits in
this workspace are validation checkpoints, not upstream GitHub history.

## Environment notes

- Host: Ubuntu 22.04.5 LTS, Linux `6.8.0-124-generic`, x86_64.
- CPU: Intel Core i7-5500U reported by the host, not an 8th generation CPU.
- RAM: 7.7 GiB total. During validation, available memory stayed above 1 GiB.
- Swap: 2.0 GiB, frequently full.
- Docker: Docker 29.7.2, Compose v5.4.0.
- Docker access: the active login session did not include the `docker` group,
  but `/etc/group` listed `omerta`; Docker commands were executed through
  `sg docker`.

## Validation matrix

| Gate | Command | Result | Evidence level | Notes |
|---|---|---:|---|---|
| Architecture tests | `.venv312/bin/python -m pytest tests/architecture -q` | 68 passed | E1 | Executed with repository Python 3.12 venv after repairs. |
| Python tests | `.venv312/bin/python -m pytest tests/ -q` | 180 passed, 2 skipped | E1/E2 | Warnings: Starlette TestClient/httpx deprecation and FastAPI `on_event` deprecation. |
| Python lint | `ruff check .` | passed | E1 | No issues reported. |
| Gateway install | `npm ci --prefix gateway` | passed | E1 | Required bundled Node 24; system Node 18 failed gateway tests. |
| Gateway build | `PATH=<bundled-node>:$PATH npm run build --prefix gateway` | passed | E1 | Bundled Node 24. |
| Gateway tests | `npm test --prefix gateway` | 2 files, 6 tests passed | E1 | Vitest. |
| Console install | `node <pnpm-11.13.1>/bin/pnpm.cjs --dir console install --frozen-lockfile` | passed | E1 | Required adding `packages: ["."]` to `console/pnpm-workspace.yaml`; the rejected `desktop-shell` workspace inclusion remains out of lockfile scope. |
| Console Prisma generate | `pnpm --dir console prisma:generate` | passed | E1 | Used the existing local placeholder `DATABASE_URL` fallback; no live DB connection claimed. |
| Console tests | `pnpm --dir console test --config vitest.config.mts` | 6 files, 11 tests passed | E1 | Warning: baseline browser mapping data is stale. |
| Console production build | `pnpm --dir console build` | passed | E1 | Warnings: unsupported Next App Router i18n config, stale baseline/caniuse data, sanitized empty DB URL logs during static generation. |
| Runtime host fmt/test | `cargo fmt --check`, `cargo test` | unavailable | blocked | No host `cargo`/`rustc`. Official Rust image did not include `cargo-fmt`/`rustup`, so fmt remains unavailable. |
| Runtime Docker cargo tests | `docker run ... rust:1.87-bookworm cargo test --locked --all-targets` | 2 passed | E1 | Ran with `CARGO_BUILD_JOBS=1`; 0 unit tests in lib/main, 2 migration contract tests passed. |
| Runtime Docker build | `docker compose ... build runtime` | passed | E2 build evidence | Built `omertaos-runtime:latest`; release build completed inside image with one Cargo job. |
| Control Docker build | `docker compose ... build control` | passed | E2 build evidence | Uses pinned `control/requirements.docker.txt` and starts HTTP plus minimal fail-closed gRPC adapter. |
| Gateway Docker build | `docker compose ... build gateway` | passed | E2 build evidence | Fastify plugins updated for Fastify 5 and WebSocket API updated. |
| Compose rendering | `docker compose --project-directory . -f deploy/docker/compose/quickstart.yml config` | passed | E1 | Syntax/interpolation only; not live acceptance. |
| CI integration placeholder | CI conditional for `tests/integration` | passed placeholder | E0 for integration | `tests/integration` directory is absent; no integration behavior was tested. |
| Bounded Bandit scan | `bandit -r control data integrations policies registry schemas shared scripts -x tests -s B101,B105` | no issues | E1 | Broad repo-wide Bandit scan was too slow and was interrupted. |
| Cargo audit | `cargo audit` | unavailable | blocked | Requires Rust/cargo and network. |
| Trivy fs scan | `trivy` | unavailable | blocked | `trivy` is not installed locally. |
| Windows bridge server | `npm ci`, `npm run build`, `npm test -- --run` | passed | E1 | 2 files, 3 tests passed. |
| Windows bridge UI | `npm ci`, `npm run build` | passed | E1 | Vite production build passed. |
| Native preflight | `bash deploy/native/scripts/preflight.sh --profile lite` | passed | N0/N1 preflight only | Read-only host check passed on Ubuntu 22.04 with systemd/cgroups v2. |
| Native env examples | `python deploy/native/env/validate.py --directory deploy/native/env` | passed | N1 static contract | Validates committed example contract only. |
| Native data env examples | `python deploy/native/env/validate_data_env.py --examples` | passed | N3 static contract | Validates committed example credential shape only; no secrets loaded. |
| Native N1 host validation | `bash deploy/native/scripts/validate-environment.sh --mode native --expected-commit 863e00c...` | failed | blocked | `/etc/omertaos` is missing and service user setup is deferred; no sudo action was taken. |

## Live Docker acceptance

Status: backend live acceptance passed with an explicit runtime-execution gap.
Console was validated by install/test/build locally, but the Console container was
not started in the live stack on this 8 GiB host.

Executed services: `postgres`, `redis`, `qdrant`, `minio`, one `runtime`,
`control`, and `gateway`.

Passing checks:

- `docker compose up -d --no-build gateway` started the backend dependency set
  without rebuilding.
- Postgres, Redis, Runtime, Control, and Gateway reached Docker `healthy`
  status where a healthcheck is defined.
- Control HTTP health returned `{"status":"ok","service":"control"}`.
- Gateway HTTP health returned `{"status":"ok","service":"gateway"}` with
  `redis` and `control` dependencies reported as `ok`.
- Control gRPC port `50051` was reachable inside `omerta-net`.
- Runtime connectivity passed with:
  `docker run --rm --network omerta-net -e AION_RUNTIME_HEALTH_ADDR=runtime:50051 omertaos-runtime:latest --healthcheck`.
- Postgres readiness passed with `pg_isready`.
- Redis readiness passed with `redis-cli ping`.
- Persistence probe survived a normal Postgres container restart:
  `codex_r4_persistence_probe.id = 'capo-r4'`.
- Gateway -> Control gRPC task submission returned HTTP 200 with application
  status `ERROR` and code `RUNTIME_TRANSPORT_UNAVAILABLE`. This proves the
  Gateway-to-Control transport is executable and fail-closed, but does not prove
  Runtime execution.
- Services were stopped with `docker compose stop`.
- Final inspected exits: Gateway 0, Control 0, Runtime 0, Postgres 0, Redis 0,
  MinIO 0, Qdrant 143; none were OOM-killed. Qdrant 143 is the upstream
  container's SIGTERM exit on normal stop.
- The `omertaos_postgres-data` and `omertaos_minio-data` Docker volumes
  remained present. No `down -v` was run.

Failed or incomplete checks:

- Full Console live health and browser path were not executed locally; Console
  was built and tested outside Docker instead.
- Runtime execution through Control remains intentionally fail-closed because
  the versioned Control-to-Runtime transport is not implemented in this
  milestone. Do not report this as successful distributed execution.

Observed warnings:

- Redis warned that `vm.overcommit_memory` is disabled. No sysctl or systemd
  change was made.
- Postgres local init log reported trust authentication for local connections in
  the default image initialization path.
- Gateway logged that TLS material and JWT public key are absent in dev
  quickstart mode. Protected task requests used the committed quickstart API-key
  path; no production auth bypass was added.

## Claim ledger comparison

| Claim | Current level | Source evidence | Executable test | Actual result | Gap |
|---|---|---|---|---|---|
| Canonical repository ownership boundaries exist | E1 | Architecture docs and tests | `pytest tests/architecture` | 68 passed | Does not prove runtime behavior. |
| Python control/data contracts are testable | E1/E2 | Python tests | `pytest tests/` | 180 passed, 2 skipped | Runtime execution remains fail-closed. |
| Gateway can build and run unit tests | E1 | Gateway package scripts | `npm run build`, `npm test` | passed | Uses bundled Node 24 because system Node 18 is too old for Vitest/Rolldown. |
| Console can install, generate Prisma client, test, and build | E1 | Console package scripts | locked pnpm install, prisma generate, unit tests, build | passed | Console live container was not started. |
| Runtime daemon can be built and tested in Docker | E1/E2 | Runtime Dockerfile and cargo tests | Compose build and Docker cargo test | passed | Host cargo fmt/test blocked; Linux isolation success not proven. |
| Quickstart compose renders | E1 | Compose file | Compose `config` | passed | Rendering is not live acceptance. |
| Backend quickstart can start | partial E2 | Compose quickstart | Start data services, Runtime, Control, Gateway | healthy | Console live container not started. |
| Gateway-to-Control task transport is executable | partial E2 | Gateway and Control containers | POST `/v1/tasks` | HTTP 200 with fail-closed `RUNTIME_TRANSPORT_UNAVAILABLE` | Control-to-Runtime execution transport not implemented. |
| Persistence survives normal restart | partial E2 | Postgres volume | Insert probe, restart Postgres, read probe | passed | App-level migrations and Console persistence not tested. |
| Distributed scheduling/runtime is implemented | E0 | Research docs mark future work | none executed | not tested | Requires Phase 7 design/implementation approval. |
| Production/native/systemd readiness | E0 | Native docs/scripts | no sudo/systemd run | not tested | Requires explicit approval for native acceptance. |

## Next blockers

1. Control-to-Runtime execution remains fail-closed; no successful Runtime task
   execution or distributed scheduling claim is supported.
2. Console live container health and Console-to-Gateway browser path remain
   unexecuted on this 8 GiB host, although Console install/test/build passed.
3. Host Rust toolchain is unavailable, and `cargo fmt --check` remains blocked.
4. Security gates that require unavailable tools (`cargo audit`, `trivy`) remain
   blocked.
5. Native N1 remains blocked until an operator approves creating `/etc/omertaos`,
   the non-login `omertaos` service user, and the clean release clone under
   `/srv/omertaos-source`.

## Phase 7 minimal runtime-scheduling prototype

Status: implemented as a local Control-owned prototype, not as distributed
cluster production evidence.

Implemented behavior:

- additive Control tables for runtime nodes, task attempts, and scheduling
  decisions;
- `/v1/runtime/nodes` registration and discovery routes;
- heartbeat updates with `healthy`, `degraded`, `unreachable`, and `draining`
  states;
- tenant, capability, capacity, freshness, and drain-state eligibility checks;
- round-robin and least-loaded placement strategies;
- bounded retry rejection and idempotent scheduling replay for an existing
  `task_id`/`attempt_id`;
- persisted scheduling-decision evidence plus audit events;
- Runtime helper registration rejects blank node IDs and resource reports no
  longer return `{}`.

Validation:

- `.venv312/bin/python -m pytest tests/control/test_runtime_scheduler.py tests/control/test_runtime_node_routes.py tests/control/test_database_migration.py -q`
  returned 8 passed with the existing FastAPI/Starlette deprecation warnings.
- `docker run --rm -e CARGO_BUILD_JOBS=1 -v "$PWD":/workspace -w /workspace/runtime-daemon rust:1.87-bookworm cargo test --locked --all-targets`
  returned 4 Runtime tests passed.

Boundaries:

- no federation, consensus, leader election, multi-region behavior, Kubernetes
  operator, or production certification is implemented;
- no successful scheduled Runtime execution is claimed;
- Runtime reports are treated as observations; Control remains the scheduler and
  policy owner.

## Native acceptance plan

Do not run these steps without explicit operator approval where noted.

1. Prepare a clean exact-commit native target.
   - Read-only: verify OS, systemd, cgroups v2, ports, disk, and tool commands
     with `preflight.sh`.
   - Requires sudo: create `/etc/omertaos` as `0750 root:root`.
   - Requires sudo: create dedicated non-login service user and group
     `omertaos`.
   - Requires operator-supplied SSH/release path: place a clean detached checkout
     of `863e00c6398bdd03a78140e9607c032a8b1025d3` under
     `/srv/omertaos-source`.
2. Render environment files.
   - Requires secret input outside Git: render `/etc/omertaos/*.env` from the
     examples with non-placeholder values.
   - Requires sudo: enforce documented modes: `omertaos.env` 0644 root:root,
     service env files 0640 root:omertaos, and `installer.env` 0600 root:root.
   - Read-only after rendering: run `validate.py --strict` and
     `validate_data_env.py`.
3. First boot and systemd installation.
   - Requires sudo and approval: install OS/data prerequisites and build native
     release with `first-boot.sh --version ... --backup ...`.
   - Reversible check before start: run install/systemd scripts with `--dry-run`
     where available.
   - Requires sudo and approval: install units with `install-systemd.sh`; this
     enables only `omertaos.target` and does not start services by itself.
4. Smoke test.
   - Requires approval to start services: start `omertaos.target`.
   - Read-only after start: run `smoke-test.sh --mode native` to verify data
     services, Runtime healthcheck, HTTP health payloads, canonical
     Console-to-Gateway-to-Control chain, listener boundaries, and journald.
5. Reboot recovery.
   - Requires approval: reboot target.
   - Read-only after boot: re-run N1 validation and native smoke test; record
     unit states and restart counts.
6. Update, rollback, backup, and restore verification.
   - Requires sudo and a verified external backup path: `backup.sh`.
   - Read-only restore verification: `restore.sh --backup ...` without
     `--apply`.
   - Requires sudo and approval: `update.sh --version ... --source ... --backup
     ...`.
   - Requires sudo and approval: `rollback.sh --check` first, then rollback only
     if operator approves activation. Database downgrades remain explicitly out
     of scope.
