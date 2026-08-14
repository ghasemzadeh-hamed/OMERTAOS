# S2.3 migration — rust-runtime to Runtime Daemon

Date: 2026-07-12

Status: unique safe behavior merged; legacy crate delegates to the canonical
crate and remains protected until S5.

## Impact analysis

- Canonical owner: `runtime-daemon/`
- Legacy input: `rust-runtime/`
- Database and public API impact: none.
- Deployment impact: canonical binary name and ports are unchanged.
- Permission/security impact: high; incomplete isolation paths now deny
  execution instead of returning synthetic success.

## Comparison result

Fourteen source files were byte-identical across the two trees and were not
copied again. The legacy `kernel-adapter/src` tree was reviewed file by file:

| Capability | Decision |
|---|---|
| Structured audit helper | Merged as `runtime-daemon/src/audit.rs` and used after capability admission |
| `ResourceQuota` model | Merged with positive-limit validation |
| cgroup, namespace, seccomp and capability-dropping adapters | Rejected as implementations because every method was an unconditional no-op |
| process bridge | Rejected because it returned PID zero without spawning |
| sandbox coordinator | Rejected because it composed the no-op adapters |
| legacy daemon main | Replaced by delegation to canonical `runtime_daemon::run()` |

The canonical crate now exposes a library and its binary calls the same run
function used by the compatibility crate. This prevents two daemon behaviors.
Vendored `protoc` selection was carried forward from the legacy build to make
canonical Rust builds independent of a system `protoc` installation.

## Security behavior

Namespace, mount, seccomp and process backends explicitly return errors until a
real Linux implementation is reviewed and tested. Capability admission can
succeed, but host execution cannot report success without isolation. Audit logs
record event, tenant, agent and outcome; commands, secrets and payloads are not
logged.

## Validation

```powershell
cargo fmt --manifest-path runtime-daemon/Cargo.toml -- --check
cargo test --manifest-path runtime-daemon/Cargo.toml --all-targets
cargo check --manifest-path rust-runtime/Cargo.toml
python -m pytest tests/architecture -q
docker compose -f docker-compose.quickstart.yml config --quiet
```

Native Linux sandbox acceptance remains pending because S2.3 deliberately does
not implement privileged isolation on this Windows host. The Structure gate
also remains expected-red while legacy roots exist.

Validation on this workstation produced:

- Rust formatting and metadata for both manifests: passed;
- static Runtime migration contract: 4 passed;
- immediate architecture invariants: 4 passed;
- full architecture suite: expected-red only at the Structure completion gate;
- Quickstart and Local Compose rendering: passed;
- Cargo test/check: blocked because `index.crates.io:443` was unreachable and
  the local cache did not contain even `anyhow`; no dependency was bypassed.

Therefore source/contract validation is complete for S2.3, but a real Cargo
compile/test and Native Linux sandbox acceptance remain mandatory gates before
Runtime production acceptance.

## Migration and rollback

No database migration is required. Revert the S2.3 commit as one unit to restore
the prior crate layout. Do not delete either Runtime tree, binaries, configuration
or persistent state. Root retirement is an S5 action requiring explicit human
review and green Native plus Quickstart acceptance.
