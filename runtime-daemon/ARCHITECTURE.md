# Runtime Daemon architecture

## Concurrency and queues

Tokio's multi-thread runtime handles gRPC, queueing, audit transport, timers, cancellation and child-process I/O. Blocking filesystem setup and wait operations use bounded blocking pools. Admission places validated jobs into bounded priority queues; overload returns resource exhaustion instead of allocating unbounded memory. Workers pull by workload class, acquire resource permits, and own one sandbox lifecycle. Per-tenant and global semaphores provide bulkheads.

## Sandbox

On Linux, a sandbox creates user/PID/mount/network namespaces, a minimal read-only root, explicit bind mounts, cgroup v2 limits, seccomp filters, dropped capabilities, `no_new_privs`, an unprivileged UID/GID, bounded environment, and controlled working directory. Network is absent unless destinations/protocols are granted. Inputs are content-addressed and mounted read-only; outputs use a dedicated quota-limited path. Cleanup is idempotent and runs after success, failure, timeout, cancellation, or daemon recovery.

## Capability enforcement

Admission verifies signature, issuer/audience, time window, task/attempt and lease binding, nonce/replay status, and supported grant version. A compiled enforcement plan intersects the request with daemon policy; intersection may only narrow access. Checks occur at admission, sandbox construction, tool/command dispatch, file/object access, network proxy, and result publication. Unsupported constraints fail closed.

## Audit pipeline

Each state change and sensitive operation emits a structured record with sequence, monotonic/wall time, daemon/node, task/attempt, grant hash, action, decision, resource label, outcome and trace ID. Records exclude secrets and raw sensitive payloads. A bounded local write-ahead spool survives exporter failure; backpressure policy distinguishes mandatory security audit from best-effort telemetry. Hash chaining and signed batches support tamper detection.

## Memory safety

Safe Rust is the default. `unsafe` is isolated, documented with invariants, and tested. All input is Protobuf-decoded with size limits; paths are canonicalized without following untrusted links; integer/resource conversions are checked; output and log buffers are capped. Child handles, mounts and cgroups use ownership guards so cleanup occurs on early return.

## Failure isolation

Jobs have separate namespaces, cgroups, directories, cancellation tokens, output quotas and audit sequences. A worker panic cannot authorize another job and is supervised. Process trees are killed via cgroup on timeout. Queue leases and attempt IDs prevent stale results. Repeated sandbox/backend failures trip node health, stop new admission, and allow Control to drain/reschedule; daemon restarts reconcile and remove orphaned sandboxes before readiness.
