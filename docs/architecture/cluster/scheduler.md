# Cluster scheduling

**Status:** design target; not implemented.

A future scheduler should map an authorized attempt to an eligible Runtime node
without bypassing policy or capability constraints. Hard constraints are
evaluated before optimization preferences.

## Candidate constraints

- tenant and trust-zone eligibility;
- required Runtime and contract version;
- isolation and tool capabilities;
- CPU, memory, accelerator, storage, and network ceilings;
- data locality and residency;
- node freshness, drain state, and active lease capacity.

## Candidate objectives

After constraints pass, placement may consider queue age, fairness, locality,
estimated startup cost, reliability, and fragmentation. Every decision should
record the rule version and inputs needed for later explanation.

## Required evidence

Evaluation should include starvation, fairness, stale capacity, concurrent
lease races, node loss, cancellation, retry safety, and deterministic replay.
No performance or scalability claim is supported until these experiments are
implemented and published.
