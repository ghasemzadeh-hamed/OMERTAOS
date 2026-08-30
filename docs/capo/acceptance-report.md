# CAPO acceptance report

## R6.9 authenticated canonical execution — 2026-08-30

Branch: `Radin/capo-r6-validation`

Validated repair commit: `cc52204` (`fix(runtime): propagate canonical dispatch
context`). Control, Gateway, and Console images were built sequentially from
that commit. The preserved isolated project used one Runtime worker, host ports
Console `13000`, Gateway `18080`, Control `18001`, and Runtime `55051`, plus the
`omerta-r6-fixed-net` network. The Control port was changed from `18000` while
diagnosing a host publishing failure; both ports exhibited the same reset.

| Gate | Result | Executable evidence and boundary |
|---|---|---|
| Context regression tests | pass | Console allowlist `2 passed`; Gateway `4 files, 9 tests passed`; targeted Control transport `7 passed`; Runtime dispatch/transport `14 passed`. Three existing Python deprecation warnings remained |
| Architecture regression | pass after stale-reference repair | The first run reported `69 passed, 1 failed, 1 deselected` because README omitted three current canonical design links. Commit `168840d` restored the references; the targeted test passed and the full rerun reported `70 passed, 1 deselected`. The intentionally red completion gate remained excluded |
| Broader Console regression | pass | `10 files, 22 tests passed` after restoring the locked pnpm `11.13.1` installation; Prisma generation and the direct Next production build exited 0 |
| Service builds | pass | Gateway and direct Console production builds passed; Control, Gateway, and Console container images then built sequentially with exit 0. The unchanged Runtime image was not rebuilt |
| Compose rendering | pass | The isolated Quickstart configuration rendered with the selected images, network, and host ports; this was treated only as static configuration evidence |
| Resource guard | pass | Available memory was 4.0 GiB before startup, 2.8 GiB during final live checks, and 3.0 GiB after shutdown, above the 1 GiB stop threshold |
| Runtime registration and heartbeat | pass, manual | `runtime-r6-1` registered inside the Control network with tenant `tenant-r6` and the single `terminal.execute` capability; a fresh heartbeat reported `healthy` |
| Authenticated canonical task | pass in constrained scope | A real NextAuth session submitted `runtime.echo.v1` through Console `/api/proxy/tasks`; Console, Gateway, Control gRPC, and one Runtime completed it with HTTP 200, application status `OK`, and an exact deterministic echo |
| Tenant and context propagation | pass | PostgreSQL recorded tenant `tenant-r6`, the submitted idempotency key, selected node `runtime-r6-1`, status `completed`, and the submitted W3C traceparent. Runtime audit recorded matching task, tenant, agent, correlation/request, trace, and `authorized`/`completed` outcomes without logging the payload |
| Same-request replay | pass in constrained scope | Repeating the authenticated request with the same idempotency key returned the same task id; PostgreSQL retained exactly one task attempt |
| Service and dependency health | pass internally | Console and Gateway host health returned valid healthy payloads; Gateway reported Redis and Control healthy; Console's system endpoint reported the Console-to-Gateway-to-Control chain healthy; Control's internal HTTP health passed |
| Quickstart smoke | partial failure | PostgreSQL, Redis, Runtime, installer, Control, Gateway, and Console container checks plus Runtime binary health passed. The next host probe failed with exit 1 because Docker's published Control port returned an empty/reset response even after isolated port change and Control recreation; internal and Gateway-to-Control probes remained HTTP 200 |
| Final shutdown | pass with note | `docker compose stop` exited 0, all services stopped, all three project volumes were preserved, and no volume-deletion command was used. Qdrant exited 143 after SIGTERM; the other running services exited 0 |

Failed toolchain attempts were not substituted silently: system Node 18 was
incompatible with the current JavaScript gates; an initial pnpm invocation
could not confirm a module purge without a TTY; the resulting partial module
state lacked Rollup's optional binary; and the pnpm build wrapper's dependency
status/network activity was interrupted with exit 130. The exact locked Console
dependencies were restored without lockfile changes, and the direct underlying
test and build commands subsequently passed. A host `python` invocation also
failed with exit 127 before acceptance orchestration began; the available
`python3` executable ran the unchanged probe successfully. Two diagnostic shell
pipelines produced misleading zero statuses after `curl` failures; neither was
accepted as evidence, and strict independent probes reproduced the failure.

This stage demonstrates one authenticated API request through the complete
canonical service path on one local worker. It does not demonstrate a browser
UI click flow, automatic Runtime registration/heartbeat, multiple workers,
scalability, successful Linux isolation, durable Control audit export,
production readiness, or security certification. The published Control host
port remains an unresolved environment/deployment gate. No credential, cookie,
token, echoed payload, or secret value was printed or recorded.

## R6.8 isolated Quickstart smoke — 2026-08-30

Branch: `Radin/capo-r6-validation`

Validated smoke repair commit:
`0c53328` (`fix(deploy): target isolated quickstart smoke`). The live run reused
the preserved single-worker `omertaos-r6-fixed` containers and images from the
R6.7 acceptance; no image build or dependency installation was performed. This
therefore validates the repaired read-only smoke probe and preserved stack, not
a fresh image build of the current branch.

| Gate | Result | Executable evidence and boundary |
|---|---|---|
| Failure reproduction | pass | The previous script rejected `--project-name` with exit 1, so it could not target the isolated acceptance project explicitly |
| Smoke contract regression | pass | `6 passed`; includes mocked project selection, isolated ports, Runtime healthcheck, installer lookup, and invalid-port rejection |
| Native contract regression | pass | `70 passed` |
| Deployment architecture regression | pass | `14 passed, 57 deselected` for the focused Quickstart/deployment/CAPO selection |
| Static validation | pass | Bash syntax, Ruff, `git diff --check`, and sanitized Compose `config --quiet` exited 0 |
| Resource guard | pass | Available memory was 2.2 GiB before startup and 1.9 GiB during live smoke, above the 1 GiB stop threshold |
| Positive isolated smoke | pass | The selected project reported healthy PostgreSQL, Redis, Runtime, Control, Gateway, and Console containers; installer exit 0; Runtime binary health; service payloads; Gateway dependencies; and the Console-to-Gateway-to-Control health chain |
| Wrong-project negative probe | pass | A nonexistent project failed with exit 1 at the missing PostgreSQL container even though the independent default-port `compose-*` stack remained healthy |
| Final shutdown | pass with note | Compose stop exited 0, persistent volumes remained present, Qdrant exited 143 after SIGTERM, and the other R6 containers exited 0 |

The smoke probe remains read-only and does not start, restart, migrate,
bootstrap, or stop services. This stage does not submit a task through Console,
prove the Console-to-Runtime execution path, validate multiple workers, or
change the existing isolation and production-readiness evidence boundaries. No
credential value was printed or recorded.

## R6 Quickstart restart persistence — 2026-08-29

Branch: `codex/capo-r5-runtime-execution`

Validated commit: `5858d3696ad30a6709b60180d2690b13baf1621b`.
The run used one Runtime worker and the preserved `omertaos-r6-fixed` volumes.
It did not build images, run benchmarks, or modify the concurrently running
`compose-*` stack. The isolated acceptance ports were Console `13000`, Gateway
`18080`, Control `18000`, and Runtime `55051`; the Docker network was
`omerta-r6-fixed-net`.

| Gate | Result | Executable evidence and boundary |
|---|---|---|
| Resource guard | pass | Available memory was 2.0 GiB before startup, 1.8 GiB at initial health, and 1.7 GiB after restart; it remained above the 1 GiB stop threshold |
| Quickstart startup | pass after two operator-configuration failures | An initial resumed command omitted the isolated network and encountered stale container network metadata; after recreation, the default Runtime port was occupied by the preserved `compose-*` stack. Reapplying the isolated network and port settings started the unchanged images successfully |
| Service health | pass | Console, Gateway, Control, Runtime, PostgreSQL, and Redis were healthy after startup and again after a complete normal stop/start cycle |
| Installer idempotency | pass | The one-shot install container exited 0 on both starts; the user-row count remained `1` |
| Prisma migration persistence | pass | Migration count remained `2`; the sanitized migration-name fingerprint remained `e2e79dd0d4a8b0bed0724ce827291103` before and after restart |
| Volume persistence | pass | PostgreSQL, MongoDB, and MinIO volumes remained present after the final `docker compose stop` |
| Final shutdown | pass with note | Compose stop exited 0; Qdrant exited 143 after SIGTERM and the other containers exited 0; no volume deletion command was used |

The failed startup attempts are environment/configuration evidence, not service
acceptance. This gate establishes restart persistence and idempotent bootstrap
for the constrained single-worker Quickstart only. It does not establish
multi-worker scalability, Linux isolation, native systemd acceptance,
production readiness, or security certification. No credential value was
printed or recorded.

## R5 constrained Runtime acceptance — 2026-08-28

Branch: `codex/capo-r5-runtime-execution`

Validated deployment/configuration commit:
`0deccc85d6ba5601fb181ce9968b6bdd23e40014`. The Runtime dispatch source is in
`711395a` and `681ff8f`; the build-context checkpoint is `d4ff77a`. Nothing in
this acceptance run was pushed or merged.

The run used one Runtime worker on the recorded 8 GB Linux host. Available
memory remained above 3 GB, services and image builds were executed
sequentially, and the existing `compose-*` stack was preserved. The R5 stack
used separate host ports and the `omerta-r5-net` network.

| Gate | Result | Executable evidence and boundary |
|---|---|---|
| Architecture regression | pass | `68 passed, 1 deselected`; the intentionally red completion gate was excluded |
| Full Python regression | pass | `203 passed, 2 skipped, 3 warnings` before live acceptance |
| Runtime image build | pass | Locked release build completed in 17 minutes; cold-build duration is not a performance benchmark |
| Runtime image identity | pass | Image ran as `runtime`; one worker became healthy on loopback port `55051` |
| Control image build | pass after transient network failure | Initial Python base-layer request returned HTTP 403; an independent pull succeeded and the unchanged rebuild passed |
| Gateway image build | blocked | First `npm ci` attempt timed out fetching locked `yargs-parser@21.1.1`; a direct URL probe later returned HTTP 200; the second attempt made no progress for 15 minutes and was stopped with exit 130 |
| Console image/live service | skipped | Gateway image gate blocked the canonical full-stack sequence; no weaker substitute was used |
| Backend startup | partial pass | PostgreSQL, Redis, one Runtime, and Control were healthy; Qdrant and MinIO were running but have no explicit Compose readiness probe |
| Control health | pass | `/health` and `/v1/health` returned `{"status":"ok","service":"control"}` on isolated host port `18000` |
| Node registration and heartbeat | pass | `runtime-r5-1` registered with `terminal.execute`, tenant `tenant-r5`, then accepted a heartbeat |
| Worker failure detection | pass in constrained scope | A heartbeat older than the 30-second threshold changed the node to `unreachable` and dispatch failed closed with `RUNTIME_NODE_UNAVAILABLE` |
| Allowlisted execution | pass | Fresh heartbeat plus gRPC Submit selected `runtime-r5-1`; `runtime.echo.v1` returned exit code 0 and `r5-audit-ok\n` |
| Context/audit propagation | pass at Runtime log boundary | Tenant, task, attempt, request, trace, actor, and authorized/completed outcomes were logged; the echoed payload was not logged |
| In-process idempotency | pass | Identical replay returned `idempotent_replay=true`; Runtime audit-event count did not increase |
| Post-restart idempotency | pass fail-closed | After normal Control restart, replay returned `RUNTIME_RESULT_REPLAY_UNAVAILABLE`; Runtime did not execute it again |
| PostgreSQL persistence | pass | A non-sensitive probe row remained readable after normal PostgreSQL restart |
| Shutdown and volume preservation | pass with note | `docker compose stop` preserved `omertaos_postgres-data` and `omertaos_minio-data`; Qdrant reported exit 143 after SIGTERM while the other R5 services exited 0 |
| Full canonical request path | blocked | Current Gateway image was unavailable, so Console -> Gateway -> Control -> Runtime was not claimed |

Runtime audit evidence required an acceptance-only Compose override setting
`RUST_LOG=info`; the host exports `RUST_LOG=warn`. Control's `emit_audit`
primitive still returns only an in-memory entry and has no durable exporter.
Successful `lite`-profile command execution is not evidence of completed Linux
namespace/seccomp isolation, production readiness, security certification, or
multi-worker scalability.

## R3 current reconciliation — 2026-08-10

Official branch `CAPO` is synchronized at evidence commit
`91921367cdfa600abb91710f7d699a183af800fa`. The current lockfiles are tracked:

| Lockfile | SHA-256 |
|---|---|
| `runtime-daemon/Cargo.lock` | `9C7EBC387FEF54CB7C2BBC70F96EA2DDF690F7636D18175FA251B96D5D5433F6` |
| `gateway/package-lock.json` | `CECAD9E18FB37754EBDF9CAC078BDC0A10CFE939365651CEB84160746866D55F` |
| `console/pnpm-lock.yaml` | `98FCA5264683D58F5274C14A62971FE56679AC7AD0C3A61C49722CFB0D4555B1` |

CI run [`31358631289`](https://github.com/Hamedghz/OMERTAOS/actions/runs/31358631289)
passed architecture, lint, all service builds, Python and locked Cargo tests,
the locked Runtime release build, integration, security, seven image builds and
six architecture-independent checks. The remaining emulated arm64 Console image
job stayed in progress for more than three hours. R3 moves arm64 image builds to
the native `ubuntu-24.04-arm` runner and retains the locked Linux Runtime binary
plus its SHA-256 as a CI artifact.

Current Gate status:

| Gate | Status | Current evidence |
|---|---|---|
| S2 Core Migration | passed | Four service builds plus locked Runtime test/release build |
| S3 Supporting Migration | passed | 63 architecture tests and deterministic retired-root guards |
| S5 Legacy Retirement | passed (repository scope) | Explicit approval, absent retired roots, no executable dependencies |
| S6 Architecture Validation | passed | Full Python and architecture suites plus CI boundaries |
| Gate R | pending | Requires the R3 commit to be clean, pushed, fully green and architecture-complete |
| Native live acceptance | pending | No current Ubuntu/systemd reboot/smoke/update/rollback/restore evidence |
| Docker live acceptance | pending | Image build is not running-stack smoke/parity evidence |

The historical report below remains immutable evidence of its original review.

> Historical snapshot: this report records the 2026-07-12 CAPO review. The
> current Native N1-N8 contract supersedes its missing-lockfile and stop/disable
> rollback descriptions. Gateway and Runtime lockfiles now exist; N8 uses
> immutable releases, canonical backup verification, and atomic code rollback.
> Live Linux/systemd, Runtime build, smoke, update, and restore acceptance remain
> pending until rerun and recorded on the intended host.

Date: 2026-07-12 (Asia/Tehran)

Branch: `capo`

Baseline: `b4021a4327d63b8db0c0e0f87267dec28907cb36`

Phase 6 head reviewed: `d4e96723b5b6341af5c3b4c899d9fdaca2054331`

## Decision

The seven-phase CAPO implementation is **conditionally accepted for human
review and Linux-host validation**. Static contracts, configuration rendering,
application entrypoint checks, Gateway/Console builds, and the verified recovery
baseline pass. Production use, permanent legacy-path retirement, merge, and
deployment are not accepted by this report.

Native systemd acceptance remains pending on the intended Debian/Ubuntu SSD
host. Running Docker Quickstart acceptance also remains pending because the
local Docker daemon did not respond during Phases 6 and 7. These two gates are
independent and neither may be inferred from static validation.

## Delivered scope

- Verified external Git/source backup and reconstruction map.
- Non-secret CAPO environment and idempotency/security contract.
- Debian/Ubuntu, PostgreSQL, and Redis installers with dry-run behavior.
- Canonical Control, Gateway, Console, and Runtime build/install scripts.
- Four non-root systemd services, aggregate target, and lifecycle scripts.
- Read-only Native/Quickstart smoke checks, contract tests, troubleshooting,
  canonical backup verification, and immutable release rollback.

Across Phases 1–6, CAPO added 29 tracked files with 1,529 lines relative to the
baseline. No existing source, schema, table, data, legacy path, or public API was
removed or moved.

## Evidence

| Check | Result | Notes |
|---|---|---|
| Backup SHA-256 and Git bundle | pass | Three hashes match; bundle reports complete history |
| CAPO Bash syntax and `--help` | pass | All reviewed scripts via Git Bash |
| CAPO PowerShell contracts | pass | Ports, env, systemd hardening, rollback, forbidden commands |
| Quickstart/Local Compose rendering | pass | Both `config --quiet` checks |
| Architecture tests | pass | `14 passed in 0.95s` in final review |
| Control import | pass | `control.app.main:app` |
| Gateway TypeScript build | pass | `tsc -p tsconfig.json` |
| Console production build | pass with warnings | Missing local Prisma generation/DB URL; stale browser data |
| Runtime metadata | pass | Cargo manifest resolves without dependency download |
| Runtime release build | blocked | `index.crates.io:443` unavailable after retries |
| Full Python regression | blocked by legacy collection | 11 import errors for removed `os.control`, `os.kernel`, `aion`, and CLI paths |
| Native Linux smoke | pending | Requires intended Linux SSD/systemd host |
| Running Quickstart smoke | pending | Docker daemon did not respond; stack was not mutated |

No coverage report was generated because CAPO changes deployment assets and
documentation rather than application runtime code.

## Security and data review

- Services run as the dedicated non-login `omertaos` account and include
  `NoNewPrivileges` and `PrivateTmp`.
- Real secrets remain outside Git in `/etc/omertaos/omertaos.env`.
- PostgreSQL and Redis are required; optional stores default disabled.
- Static scanning found no executable destructive disk, Git move/removal,
  `DROP`, or `TRUNCATE` command in CAPO assets.
- Rollback preserves source, configuration, accounts, databases, volumes, and
  persistent state.

## Open acceptance gates

1. Run installers twice on a disposable Debian/Ubuntu SSD host and confirm the
   second execution is idempotent.
2. Run `first-boot.sh --version VERSION --backup PATH --start`, Native smoke,
   journald review, reboot recovery, stop/start, update, and rollback
   preview/execute with an operator present.
3. Start Quickstart, run its smoke test, verify Console → Gateway → Control →
   Runtime, and stop it without deleting volumes.
4. Restore the external backup in an isolated environment and reconcile the
   resulting commit and data checks.
5. Resolve or formally quarantine the legacy Python tests before treating the
   repository-wide regression suite as green.

Until all relevant gates pass, the permanent-deletion gate stays closed and
human review is required before merge or any production use.
