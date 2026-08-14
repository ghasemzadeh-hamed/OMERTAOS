# OMERTAOS Agent Instructions

You are working inside the OMERTAOS repository.

Scope note: Codex discovers repository instructions from the Git root down to
the working directory. The root `AGENTS.md` is therefore the canonical
repository contract. This file adds guidance only while working inside
`.codex/`.

## Execution Default

- A user request to implement, fix, change, refactor, build, complete, or
  continue means proceed from focused inspection to a safe patch and targeted
  validation in the same task.
- Give the required impact analysis as a short progress update; do not stop and
  wait after it unless a material choice or additional authority is required.
- Never create a plan, status report, task board, or other Markdown file as a
  substitute for requested code/config/test work.
- Documentation is conditional: update it only for public behavior, API,
  schema/migration, setup/configuration, architecture contract, or operator
  workflow changes. Prefer updating an existing relevant document.

## Project Identity

OMERTAOS / AION is a Hybrid Agent OS project.

Primary architecture:

Console / Next.js
    -> Gateway / Fastify
    -> Control / Python
    -> Runtime Daemon / Rust
    -> Agent Execution / Sandbox / Tools

Data Layer:
Postgres + Redis + Mongo + Qdrant + MinIO

Policy / Registry:
Policies + Model Profiles + Agent Registry + Schemas

## Branch And Workflow Focus

- Stay on the currently checked-out branch unless the user explicitly requests
  a branch change.
- A named phase ledger applies only to a task that explicitly invokes it. Do not
  use `.codex/TASKS.md` or a historical CAPO ledger as an automatic work queue.
- Native and Quickstart compatibility remain important, but the current task
  and current canonical ownership contract determine the implementation scope.

## Core Behavior

- Preserve the current architecture.
- Do not rewrite the whole system.
- Do not restore retired migration roots or create parallel owners.
- Prefer small, reviewable changes.
- Keep backward compatibility where possible.
- Do not introduce unnecessary dependencies.
- Do not expose secrets, tokens, API keys, credentials, private paths, or .env values.
- Do not claim live validation passed unless commands were actually run.
- When changing Docker, Compose, setup, or runtime scripts, keep Windows and Linux compatibility in mind.

## Critical Architecture Rules

The target execution path must remain:

Console -> Gateway -> Control -> Runtime Daemon

Rules:
- Console must talk to Gateway, not directly to Control.
- Gateway is the API boundary.
- Control is the Python decision and orchestration owner.
- Runtime Daemon is the Rust execution boundary.
- Runtime execution must remain separated from UI and Gateway logic.
- Data, Policy, Registry, Schemas, and Observability layers must remain behind this path.

## Protected Canonical Paths

Never delete these paths unless explicitly approved and verified with Git history and architecture tests:

- .github/
- console/
- gateway/
- control/
- runtime-daemon/
- data/
- registry/
- schemas/
- shared/
- policies/
- integrations/
- deploy/
- scripts/
- tests/
- docs/

Retired-root names belong only in the centralized architecture fixture and
historical ADR/migration evidence. They must not reappear as tracked top-level
paths, imports, runtime references, or current `.codex` guidance.

Never delete maintained root setup files:

- docker-compose.yml
- quick-install.sh
- quick-install.ps1
- install.sh
- install.ps1
- uninstall.sh
- uninstall.ps1
- .env.example
- pyproject.toml
- requirements.txt
- Makefile
- README.md

## Before Changing Code

1. Inspect current structure.
2. Identify affected files.
3. Check imports, references, package scripts, Docker paths, and tests.
4. Explain the intended change.
5. Apply the smallest safe patch without waiting after the explanation unless
   a real blocker requires user input.
6. Run available validation commands.
7. Report risks honestly.

## Final Response Format

### Summary
What changed.

### Files Changed
List changed files.

### Validation
Commands run and results.

### Risks / Notes
Incomplete, risky, or manually verified areas.

### Next Step
One concrete next action.

Keep this final report concise. Do not create a separate report file unless the
user explicitly requests one.
