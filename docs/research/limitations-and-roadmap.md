# Limitations and validation roadmap

**Document role:** explicit limitations and evidence-driven next work.

## Current limitations

### Runtime isolation

Linux namespace, mount, seccomp, and isolated-process backends currently return
errors. This is intentionally fail-closed, but it means successful sandboxed
execution has not been demonstrated. Signature checking is also insufficient
for a production capability-grant protocol.

### Distributed operation

Control contains a minimal local Runtime node registry and scheduler prototype,
and Runtime exposes bounded registration/resource-report helpers. Authenticated
membership, cross-Control failure detection, leader election, federation,
partition handling, consistency behavior, signed grants, and successful
scheduled Runtime execution remain incomplete.

### Empirical performance

No controlled latency, throughput, scalability, fairness, or resource-overhead
dataset is committed. Performance language in architecture documents is a
target until benchmark artifacts are published.

### Security assurance

Repository boundaries, negative-path tests, dependency scans, and secure
defaults are useful engineering controls. They are not a formal proof,
penetration test, certification, or guarantee against kernel, operator,
supply-chain, side-channel, or model-level attacks.

### Deployment acceptance

Compose rendering and static installation checks do not establish a working
deployment. Native Linux/systemd and running Quickstart acceptance remain
separate gates, as recorded in the CAPO acceptance material.

### External validity

The architecture has not yet been evaluated across independent organizations,
production workloads, heterogeneous clusters, or adversarial multi-tenant
environments.

## Roadmap ordered by evidence value

1. Implement the Runtime sandbox backends and cryptographic grant verification.
2. Add negative escape, path, network, resource, cancellation, and cleanup
   tests on a compatible isolated Linux runner.
3. Complete a pinned Quickstart acceptance run and a Native Linux/systemd
   install/rollback run.
4. Implement traceable tenant/audit propagation tests across the full request
   path.
5. Publish benchmark workloads, seeds, raw observations, environment manifests,
   and analysis notebooks/scripts.
6. Add fault-injection experiments for Runtime loss, queue failure, provider
   timeout, persistence outage, and partial network partition.
7. Implement and evaluate membership/scheduling only after single-node safety
   and acceptance gates pass.
8. Request independent architecture, security, and reproducibility review.

## Exit criteria

A limitation may be removed only when:

- the implementation is present in the canonical owner;
- positive and negative tests are reproducible;
- the environment and exact commit are recorded;
- failures and skipped cases are reported;
- documentation and manuscript wording are updated together.

Roadmap completion should never be inferred from the existence of a heading,
stub, health endpoint, CI job, or design diagram.
