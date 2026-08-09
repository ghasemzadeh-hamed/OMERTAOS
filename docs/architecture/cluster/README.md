# Cluster architecture notes

**Document role:** design target with minimal prototype scaffolding.

Cluster orchestration belongs to `control/`; host execution and isolation
belong to `runtime-daemon/`. These notes preserve the former cluster topics
without creating a third orchestration owner.

## Current implementation status

The Runtime contains two minimal helpers:

- `cluster/node_registration.rs` accepts a node identifier and currently
  returns `true`;
- `cluster/resource_report.rs` currently returns an empty JSON object.

There is no implemented membership protocol, failure detector, distributed
scheduler, federation protocol, leader election, lease fencing, or
partition-recovery mechanism. The topic documents below are specifications for
future work, not operational instructions or evidence of a working cluster.

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
