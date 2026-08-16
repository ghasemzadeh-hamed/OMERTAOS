# Cluster scheduling

**Status:** minimal local prototype.

The current `control/scheduling/` prototype maps a requested attempt to an
eligible Runtime node using local Control state. It evaluates hard constraints
before optimization preferences and records each scheduling decision. It does
not yet execute the attempt, mint a signed Runtime grant, coordinate multiple
Control instances, or prove failover behavior.

## Candidate constraints

- tenant and trust-zone eligibility;
- required Runtime and contract version;
- isolation and tool capabilities;
- CPU, memory, accelerator, storage, and network ceilings;
- data locality and residency;
- node freshness, drain state, and active lease capacity.

## Candidate objectives

After constraints pass, the prototype supports round-robin and least-loaded
placement. Future placement may consider queue age, fairness, locality,
estimated startup cost, reliability, and fragmentation. Every decision should
record the rule version and inputs needed for later explanation.

## Required evidence

Evaluation should include starvation, fairness, stale capacity, concurrent
lease races, node loss, cancellation, retry safety, and deterministic replay.
No performance or scalability claim is supported until these experiments are
implemented and published.
