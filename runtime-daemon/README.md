# Runtime Daemon

The Runtime Daemon is the Rust execution boundary for OMERTAOS agents. It accepts authorized jobs from the Control Plane over gRPC, verifies task-bound capability grants, queues work, executes it in an isolated sandbox, emits audit events, and returns structured results.

```text
gRPC admission → grant verification → bounded job queue → worker
               → sandbox + resource limits → command/tool adapter
               → audit/result stream → cleanup
```

Responsibilities include sandbox creation, process and command execution, filesystem/network/device capability enforcement, CPU/memory/time/process limits, cancellation, output bounds, cleanup, and tamper-evident audit records. It does not authenticate end users, plan tasks, or choose agents/models.

Security is deny-by-default. A job must carry a valid signature, audience, expiry, task/attempt binding, lease token, executable allowlist, path/network rules, and resource ceilings. Linux deployments combine namespaces, cgroups, mount restrictions, seccomp and privilege dropping; platform-specific backends must provide equivalent semantics or reject unsupported grants.

The daemon targets low queue overhead and high throughput through Tokio asynchronous I/O, bounded multi-thread scheduling, backpressure, streaming output, prevalidated sandbox templates, and separate pools for workload classes. Performance never bypasses grant verification or cleanup.

Build and test:

```bash
cargo build --manifest-path runtime-daemon/Cargo.toml --release
cargo test --manifest-path runtime-daemon/Cargo.toml
```

The local quickstart builds the daemon as the `runtime` service and binds gRPC to
`127.0.0.1:50051`. Containers reach it at `runtime:50051`. Override
`AION_RUNTIME_BIND_ADDR` only when running the binary outside Compose.
The container healthcheck uses `runtime-daemon --healthcheck` to verify that the
configured gRPC listener accepts connections before dependent services start.

Expose the gRPC listener only on the internal service network and require mTLS in production.

## Current execution gate

The canonical server, capability checks and health endpoint are available, but
the Linux namespace, mount, seccomp and isolated-process backends are not yet
implemented. Execution therefore fails closed instead of returning a synthetic
PID or command success. Do not treat gRPC readiness as sandbox acceptance.

The legacy `rust-runtime` package is a compatibility binary that delegates to
this crate. It contains no independent daemon entrypoint. Permanent removal of
that wrapper remains gated on Structure S5 and Native/Quickstart acceptance.
