# Manuscript alignment

**Document role:** alignment map for draft research manuscripts. It does not
state that a manuscript has been submitted, accepted, or published.

## Journal-oriented tracks

| Track | Primary contribution | Strongest repository evidence | Evidence still required |
|---|---|---|---|
| System-software architecture | Modular Control/Runtime separation and canonical ownership | Architecture tests, ADR, source topology, versioned boundaries | Comparative architecture evaluation and complete Runtime acceptance |
| Distributed runtime infrastructure | Governed execution path and reproducible benchmark decomposition | Service boundaries, Compose models, Runtime interface, benchmark protocol | Executed scalability, latency, failure, and resource-isolation experiments |
| Security-by-architecture | Policy/admission separation, capability checks, tenant-aware audit design | Gateway/Control/Runtime ownership, negative-path Runtime tests, security requirements | Cryptographic grant implementation, Linux isolation tests, threat-driven penetration testing |

## Shared factual core

All manuscript variants should agree on these facts:

- OMERTAOS is a research prototype and reference architecture.
- The canonical path is Console -> Gateway -> Control -> Runtime.
- Architecture-level repository gates exist.
- Runtime isolation backends are incomplete and currently fail closed.
- Distributed cluster behavior is not implemented beyond minimal scaffolding.
- Quantitative benchmark results are not yet committed.
- There is no claim of formal verification, regulatory compliance, security
  certification, or production acceptance.

## Recommended manuscript evidence links

Use immutable GitHub links that include the evaluated commit SHA for:

- `README.md` and `docs/research/evidence-and-claims.md`;
- architecture tests under `tests/architecture/`;
- Runtime negative-path tests and sandbox backends;
- `ARCHITECTURE.md`, `STRUCTURE.md`, and ADR 0001;
- the exact benchmark scripts and raw data when those artifacts are added.

Do not cite a moving branch URL as the sole reproducibility reference.

## Metadata before submission

Each manuscript should be checked for:

- complete author name and affiliation;
- corresponding-author email;
- ORCID where available;
- conflict-of-interest and funding statements;
- data/code availability language matching the actual repository state;
- journal-specific word, figure, reference, and anonymization requirements.

Missing email or ORCID values must remain explicit placeholders in private
drafts; they must never be guessed. Private Drive drafts and reviewer
correspondence should not be linked from this public repository.

## Consistency review

Before any submission:

1. pin the repository commit evaluated by the manuscript;
2. rerun the reproducibility protocol;
3. reconcile every result statement with the claim ledger;
4. move new quantitative results from E0/E3 to E1/E2 only when raw artifacts
   and analysis are reviewable;
5. update limitations and availability statements;
6. have a domain expert independently review security and performance claims.
