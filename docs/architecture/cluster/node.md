# Cluster node model

**Status:** minimal Control-owned prototype plus Runtime reporting helpers.

A future node record should identify an immutable node identity, software and
contract versions, supported execution backends, capacity, labels, trust zone,
last observation, and current eligibility. Resource reports must be signed or
authenticated, bounded, freshness-checked, and treated as observations rather
than unquestioned truth.

The current prototype covers only the first local slice of this specification:

- Control can persist node registration and heartbeat observations;
- Control marks stale nodes unreachable and can place nodes in draining state;
- Runtime helper registration rejects blank identifiers;
- Runtime resource reporting returns a bounded local JSON capacity snapshot.

It must not be used as evidence of authenticated cluster membership,
multi-Control coordination, node trust, production capacity management, or
multi-node execution.

## Safety requirements

- node identity cannot be supplied by an untrusted workload;
- a node cannot self-authorize tenant or task access;
- stale capacity and heartbeats make a node ineligible;
- incompatible contract or Runtime versions fail closed;
- decommissioning fences existing leases before capacity is reassigned.
