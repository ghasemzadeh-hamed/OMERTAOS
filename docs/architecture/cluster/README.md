# Cluster architecture notes

The former root `cluster/` contained placeholder headings only. Cluster
orchestration belongs to `control/`; host execution and isolation belong to
`runtime-daemon/`. The preserved topic files in this directory are architecture
notes, not implemented services or alternate owners.
**Document role:** design target with minimal prototype scaffolding.

Cluster orchestration belongs to `control/`; host execution and isolation
belong to `runtime-daemon/`. These notes preserve the former cluster topics
without creating a third orchestration owner.

## Current implementation status

The Runtime contains two minimal helpers:

- `cluster/node_registration.rs` accepts a node identifier and currently
  rejects blank identifiers;
- `cluster/resource_report.rs` reports a bounded local node/capacity snapshot
  from process environment and host parallelism.

Control contains a minimal prototype under `control/scheduling/` and
`control/app/runtime_nodes/` for node registration, heartbeat freshness,
draining/unreachable states, tenant/capability/capacity eligibility,
round-robin/least-loaded placement, bounded retry checks, and persisted
scheduling-decision evidence.

There is no implemented distributed membership protocol, consensus, federation
protocol, leader election, cross-Control lease fencing, or partition-recovery
mechanism. The topic documents below are specifications for future work, not
operational instructions or evidence of a production cluster.

## Topics

- [Control ownership](control.md)
- [Node model](node.md)
- [Membership](membership.md)
- [Scheduling](scheduler.md)
- [Federation](federation.md)

## Required entry gate

Cluster implementation should begin only after single-node Runtime isolation,
capability verification, audit propagation, Quickstart acceptance, and failure
cleanup are reproducibly validated. Distributed execution must not weaken the
canonical `Console -> Gateway -> Control -> Runtime` trust path.
