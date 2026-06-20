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

Expose the gRPC listener only on the internal service network and require mTLS in production.
