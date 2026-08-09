# OMERTAOS research package

This directory provides an evidence-oriented view of OMERTAOS for academic
review. It translates the repository into research questions, falsifiable
claims, implementation evidence, experimental procedures, and known
limitations.

## Scope

OMERTAOS studies a layered architecture for governed agentic-AI execution:

```text
presentation -> admission -> orchestration -> privileged execution
```

The central hypothesis is that an explicit Control/Runtime boundary can improve
reasoning about authorization, tenant isolation, observability, failure
containment, and reproducibility compared with designs where an orchestrator
directly invokes host tools.

## Documents

1. [Research positioning](research-positioning.md) defines the problem,
   research questions, architectural contribution, and evaluation units.
2. [Evidence and claims](evidence-and-claims.md) labels each major claim as
   verified, prototyped, or planned.
3. [Reproducibility](reproducibility.md) describes environments, commands,
   expected interpretation, and artifact capture.
4. [Manuscript alignment](manuscript-alignment.md) maps the repository to three
   journal-oriented narratives without claiming submission acceptance.
5. [Limitations and roadmap](limitations-and-roadmap.md) records open technical
   and empirical gaps.

## Evaluation rule

Every scientific statement should be traceable to one of:

- a versioned source file;
- an executable test or static contract;
- a dated validation report tied to a commit;
- an explicitly labelled experimental plan.

Architecture diagrams and requirements are not treated as empirical results.
Synthetic examples are not treated as production workloads. A health endpoint
proves service readiness only at the scope implemented by that endpoint.

## Current maturity

OMERTAOS presently offers a canonical multi-plane repository, architecture
gates, service prototypes, deployment definitions, and a fail-closed Runtime
migration boundary. It does not yet offer completed Linux sandbox
implementation, distributed membership/federation protocols, controlled
benchmark results, production acceptance evidence, formal verification, or an
independent penetration-test report.

Reviewers should begin with the
[claim ledger](evidence-and-claims.md) before interpreting feature-oriented
documents elsewhere in the repository.
