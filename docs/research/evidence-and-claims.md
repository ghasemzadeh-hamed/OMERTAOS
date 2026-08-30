# Evidence and claims

**Document role:** current claim ledger for academic and technical review.

## Evidence levels

| Level | Definition |
|---|---|
| **E1 — repository-verified** | The claim is checked by an executable repository test or deterministic static gate. |
| **E2 — implemented prototype** | Relevant source and targeted checks exist, but the complete deployment or acceptance path has not been demonstrated. |
| **E3 — design target** | The repository documents the behavior, but implementation or empirical validation is incomplete. |
| **E0 — unsupported** | No adequate evidence is present; the statement must not be presented as a result. |

## Claim ledger

| Claim | Level | Repository evidence | Boundary of the claim |
|---|---|---|---|
| The canonical request path is Console -> Gateway -> Control -> Runtime. | E1 | `tests/architecture/test_layer_boundaries.py`, `test_canonical_contract.py`, `STRUCTURE.md` | Proves repository dependencies and selected routes, not network segmentation in a deployed cluster. |
| Canonical top-level ownership replaced migration-era duplicate roots. | E1 | `tests/architecture/test_target_structure.py`, Structure S6 report | Applies to the evaluated tree/commit; historical material remains under migration evidence. |
| Control does not directly execute host subprocesses. | E1 | `tests/architecture/test_subprocess_boundaries.py` | Static and targeted source scope; not a formal whole-program proof. |
| Runtime denies execution when required sandbox backends are unavailable. | E2 | `runtime-daemon/src/sandbox/*.rs`, `runtime-daemon/tests/migration_contract.rs` | Demonstrates fail-closed stubs; it does not demonstrate successful isolated execution. |
| Runtime checks named capabilities before selected RPC operations. | E2 | `runtime-daemon/src/security/capability.rs`, `server.rs` | Current signature validation is minimal and does not establish a production cryptographic grant protocol. |
| Gateway and Control form separate transport/orchestration services. | E2 | `gateway/`, `control/`, versioned contracts, service tests/builds | Full end-to-end production acceptance remains pending. |
| Control contains a minimal Runtime node registry, local lifecycle supervisor, and scheduler prototype. | E2 | `control/scheduling/`, `control/app/runtime_nodes/`, scheduler/lifecycle tests, R5 and R6.10 constrained acceptance reports | Demonstrates single-Control registration, bounded probe-driven heartbeat, stale-worker detection, automatic local recovery, eligibility, round-robin/least-loaded selection, bounded retry and scheduling evidence. Declared capacity is static local configuration. It does not prove distributed membership, consensus, leader failover, lease fencing, or multi-worker scalability. |
| The allowlisted `runtime.echo.v1` path can execute through the authenticated canonical service path on one local Runtime worker. | E2 | R5 commits `711395a`, `681ff8f`; R6.9 commit `cc52204`; R6.10 commit `ac39d51`; `docs/capo/acceptance-report.md` | Constrained live runs demonstrated selection, execution, authenticated Console API -> Gateway -> Control -> Runtime traversal, tenant/correlation/trace/idempotency propagation, Runtime audit fields, same-request replay, probe-driven local worker registration/recovery, outage rejection, and fail-closed post-restart replay. Browser UI traversal, multiple workers, durable Control audit export, production isolation, and broader commands remain unproven. |
| The system provides complete Linux namespace, mount, seccomp, and process isolation. | E0 | Backends currently return errors | Must not be claimed until implementation and negative/escape testing pass on a compatible Linux host. |
| OMERTAOS provides distributed membership, scheduling, and federation. | E0 | Cluster documents plus minimal node-registration/resource-report stubs | These are design topics, not a working distributed subsystem. |
| OMERTAOS has measured scalability or lower latency than alternatives. | E0 | Benchmark blueprint only | No controlled quantitative results are committed. |
| OMERTAOS is security-certified, formally verified, or penetration-tested. | E0 | No certification or independent report | Architecture and CI scans are not certification. |
| Native Linux/systemd and running Quickstart paths have passed production acceptance. | E0 | CAPO acceptance report records pending gates | Static checks and Compose rendering are insufficient. |

## Acceptable wording

Use:

- “the architecture tests reject selected bypass paths”;
- “the Runtime prototype currently fails closed when isolation backends are
  unavailable”;
- “the repository defines a benchmark protocol”;
- “one constrained local worker executed the allowlisted Runtime echo path”;
- “the design targets tenant-aware auditability.”

Do not use without new evidence:

- “provably secure”;
- “production-ready”;
- “fully isolated”;
- “horizontally scalable”;
- “low latency” or “high throughput”;
- “validated in real-world deployments.”

## Evidence provenance

Results should record:

- repository URL and exact commit SHA;
- branch only as navigation context, not as a stable identifier;
- operating system, architecture, toolchain, and dependency lock state;
- exact command and exit code;
- test counts, skipped tests, warnings, and unavailable external services;
- generated logs or reports with secrets removed.

The dated migration and CAPO reports are useful provenance but may become stale.
Current reviewers should rerun the commands in
[Reproducibility](reproducibility.md).
