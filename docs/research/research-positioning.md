# Research positioning

**Document role:** research framing, not empirical evidence.

## Problem

Agentic-AI systems combine probabilistic planning with deterministic software
and privileged tools. When planning, authorization, persistence, and host
execution are collapsed into one process, it becomes difficult to establish
least privilege, isolate tenants, reproduce failures, or attribute side
effects. OMERTAOS explores whether a layered system-software architecture can
make these boundaries explicit and testable.

## Research questions

| ID | Question | Evaluation unit |
|---|---|---|
| RQ1 | Can architecture rules prevent presentation and orchestration code from bypassing the intended execution boundary? | Import/path contracts and request-flow tests |
| RQ2 | Can a Runtime reject execution when required capabilities or isolation mechanisms are absent? | Negative-path Runtime tests |
| RQ3 | Can identity, tenant, task, attempt, and correlation context remain attributable across service boundaries? | Contract and audit-field tests |
| RQ4 | What latency and throughput overhead does the governance path introduce relative to model and tool latency? | Controlled benchmark campaign |
| RQ5 | How does the architecture behave under worker, provider, queue, and persistence failures? | Fault-injection scenarios |

RQ1 has repository-level evidence. RQ2 has partial fail-closed prototype
evidence. RQ3 is represented in contracts and architecture requirements but
needs broader end-to-end validation. RQ4 and RQ5 remain experimental work.

## Architectural contribution

The canonical decomposition is:

- **Console:** presentation and operator interaction;
- **Gateway:** external authentication, admission, validation, and streaming;
- **Control:** planning, policy decisions, scheduling, durable lifecycle, and
  aggregation;
- **Runtime Daemon:** capability enforcement and privileged host execution;
- **Data/Registry/Policies:** typed state, metadata, and policy owners;
- **Schemas/Shared:** versioned contracts and generated bindings.

The intended contribution is the explicit ownership and trust-boundary model,
plus repository rules that make common bypasses detectable. The project does
not claim novelty for individual technologies such as FastAPI, Fastify, Rust,
Redis, PostgreSQL, or gRPC.

## Unit of comparison

A credible comparison should evaluate architecture variants under the same
model provider, tool implementation, workload, hardware, and network:

1. direct in-process tool invocation;
2. gateway plus orchestration without a separate Runtime;
3. the OMERTAOS four-plane path.

Measurements should separate:

- admission and schema-validation time;
- policy-decision time;
- queue and scheduling delay;
- Runtime dispatch and sandbox startup;
- external model/tool latency;
- persistence and audit overhead.

Without this decomposition, an end-to-end number cannot attribute overhead to
the architecture itself.

## Threat and trust model

The research design assumes untrusted or fallible task input, potentially
compromised tools, tenant separation requirements, and trusted platform
operators. Gateway, Control, Runtime, secret providers, and data stores are
separate trust zones. The current repository does not prove resistance to a
malicious host administrator, kernel compromise, supply-chain compromise, or
side-channel attacks.

## Success criteria

The architecture would be supported by evidence if:

- forbidden dependency and bypass paths fail deterministic tests;
- unauthorized or underspecified execution fails closed;
- audit records allow an attempt to be reconstructed without exposing secrets;
- controlled experiments report governance overhead and confidence intervals;
- fault injection demonstrates bounded, attributable failure behavior;
- independent reviewers can reproduce the results from a pinned commit.

Current evidence satisfies only a subset of these criteria. The remaining work
is listed in [Limitations and roadmap](limitations-and-roadmap.md).
