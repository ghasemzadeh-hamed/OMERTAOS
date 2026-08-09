# Cluster node model

**Status:** minimal Runtime scaffolding only.

A future node record should identify an immutable node identity, software and
contract versions, supported execution backends, capacity, labels, trust zone,
last observation, and current eligibility. Resource reports must be signed or
authenticated, bounded, freshness-checked, and treated as observations rather
than unquestioned truth.

The present helpers do not meet this specification:

- registration returns success without persistence or authentication;
- resource reporting returns `{}`.

They must not be used as evidence of discovery, health, capacity management, or
multi-node execution.

## Safety requirements

- node identity cannot be supplied by an untrusted workload;
- a node cannot self-authorize tenant or task access;
- stale capacity and heartbeats make a node ineligible;
- incompatible contract or Runtime versions fail closed;
- decommissioning fences existing leases before capacity is reassigned.
