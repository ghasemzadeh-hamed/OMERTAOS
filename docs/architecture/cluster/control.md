# Cluster control ownership

**Status:** design target; no separate cluster-control service is implemented.

Control remains the sole owner of distributed orchestration decisions. A future
cluster subsystem may provide internal modules for placement, leases, failure
recovery, and capacity accounting, but it must not become an alternate public
API or execute host operations.

## Responsibilities

- maintain the authoritative node and lease state;
- select eligible nodes using policy, capability, locality, and resource data;
- issue attempt-scoped, time-bounded execution grants;
- fence expired leases and reconcile uncertain outcomes;
- persist scheduling decisions and emit auditable lifecycle facts.

Runtime nodes may report capabilities and enforce an assigned grant. They must
not select tenants, agents, models, or policy outcomes.

## Required evidence

Implementation requires deterministic lease/fencing tests, stale-node and
duplicate-attempt tests, partition scenarios, authorization tests, and
traceability from scheduling decision to Runtime audit record.
