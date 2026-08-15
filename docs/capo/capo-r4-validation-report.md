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
| Architecture tests | `python -m pytest tests/architecture -q` | 63 passed | E1 | Executed with bundled Python 3.12 venv. |
| Python tests | `python -m pytest tests/ -q` | 173 passed, 2 skipped | E1/E2 | Warnings: Starlette TestClient/httpx deprecation and FastAPI `on_event` deprecation. |
| Python lint | `ruff check .` | passed | E1 | No issues reported. |
| Gateway install | `npm ci --prefix gateway` | passed | E1 | Required bundled Node 24; system Node 18 failed gateway tests. |
| Gateway build | `npm run build --prefix gateway` | passed | E1 | Bundled Node 24. |
| Gateway tests | `npm test --prefix gateway` | 2 files, 6 tests passed | E1 | Vitest. |
| Console install | `pnpm --dir console install --frozen-lockfile` | failed | blocked | Registry/network timeouts while fetching packages such as `next`, `@prisma/client`, and `@next/swc-linux-x64-gnu`. Console tests/build were skipped because installation was incomplete. |
| Runtime host fmt/test | `cargo fmt --check`, `cargo test` | unavailable | blocked | No host `cargo`; local rustup 1.87.0 install was stopped after slow/incomplete component downloads. |
| Runtime Docker build | `docker compose ... build runtime` | passed | E2 build evidence | Built `omertaos-runtime:latest`; release build completed inside image. This is not a substitute for host cargo fmt/test. |
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

Status: partial backend acceptance only.

Executed services: `postgres`, `redis`, and one `runtime` container. Console,
Gateway, Control, MinIO, Qdrant, and Mongo were not started.

Passing checks:

- `docker compose up -d --no-build postgres redis runtime` exited 0.
- Postgres, Redis, and Runtime reached Docker `healthy` status.
- Runtime connectivity passed with:
  `docker run --rm --network omerta-net -e AION_RUNTIME_HEALTH_ADDR=runtime:50051 omertaos-runtime:latest --healthcheck`.
- Postgres readiness passed with `pg_isready`.
- Redis readiness passed with `redis-cli ping`.
- Persistence probe survived a normal Postgres container restart:
  `codex_acceptance_probe.id = 'capo-r4-live-probe'`.
- Services were stopped with `docker compose stop postgres redis runtime`.
- The `omertaos_postgres-data` Docker volume remained present. No `down -v` was run.

Failed or incomplete checks:

- Control image build failed during `pip install` with a
  `files.pythonhosted.org` read timeout while downloading `psycopg2-binary`.
- Because Control did not build, Gateway/Control/Runtime live request flow was
  not executed.
- Console live health and Console-to-Gateway path were not executed.
- Runtime container stopped with exit code 137 after `docker compose stop`;
  Postgres and Redis stopped with exit code 0. Treat runtime graceful shutdown as
  not proven.

Observed warnings:

- Redis warned that `vm.overcommit_memory` is disabled. No sysctl or systemd
  change was made.
- Postgres local init log reported trust authentication for local connections in
  the default image initialization path.

## Claim ledger comparison

| Claim | Current level | Source evidence | Executable test | Actual result | Gap |
|---|---|---|---|---|---|
| Canonical repository ownership boundaries exist | E1 | Architecture docs and tests | `pytest tests/architecture` | 63 passed | Does not prove runtime behavior. |
| Python control/data contracts are testable | E1/E2 | Python tests | `pytest tests/` | 173 passed, 2 skipped | Live services not covered by this gate. |
| Gateway can build and run unit tests | E1 | Gateway package scripts | `npm ci`, `npm run build`, `npm test` | passed | Live Gateway not started because Control build failed. |
| Runtime daemon can be built into a container image | E2 build evidence | Runtime Dockerfile | Compose build of `runtime` | passed | Host cargo fmt/test blocked; Linux isolation success not proven. |
| Quickstart compose renders | E1 | Compose file | Compose `config` | passed | Rendering is not live acceptance. |
| Minimal data/runtime services can start | partial E2 | Compose quickstart | Start Postgres, Redis, Runtime | healthy | Control/Gateway/Console path not executed. |
| Persistence survives normal restart | partial E2 | Postgres volume | Insert probe, restart Postgres, read probe | passed | App-level migrations and Console persistence not tested. |
| Distributed scheduling/runtime is implemented | E0 | Research docs mark future work | none executed | not tested | Requires Phase 7 design/implementation approval. |
| Production/native/systemd readiness | E0 | Native docs/scripts | no sudo/systemd run | not tested | Requires explicit approval for native acceptance. |

## Next blockers

1. Network instability blocks reproducible Console and Control dependency
   installation.
2. Host Rust toolchain is unavailable; local rustup download was too slow to
   complete in this run.
3. Runtime shutdown under Compose ended with exit 137 and needs diagnosis before
   claiming clean graceful shutdown.
4. Full Console -> Gateway -> Control -> Runtime acceptance remains blocked until
   Control and Gateway images build and start.
5. Native N1 remains blocked until an operator approves creating `/etc/omertaos`,
   the non-login `omertaos` service user, and the clean release clone under
   `/srv/omertaos-source`.

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
