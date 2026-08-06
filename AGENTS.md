# OMERTAOS Engineering Instructions

These instructions apply to the whole repository. The user's current request is
the source of task scope; historical plans, task boards, and status documents do
not authorize work by themselves.

## Execution default

- Treat `implement`, `fix`, `change`, `refactor`, `build`, `complete`, and
  `continue` requests as authorization for focused, non-destructive edits and
  validation inside the requested scope.
- Inspect the relevant files first, send a short impact analysis as a progress
  update, then continue to the patch and tests in the same task. The impact
  analysis is not a stopping gate.
- Do not replace implementation with a plan, checklist, audit, task board, or
  Markdown report. Create a planning document only when the user explicitly
  requests planning/documentation-only work or an active phase contract names
  that document as the deliverable.
- For `review`, `explain`, `audit`, or `diagnose` requests, remain read-only
  unless the user also asks for fixes.
- Ask a blocking question only when a missing choice would materially change
  the result or when additional authority is required. Otherwise make a safe,
  stated assumption and proceed.
- If implementation is blocked, report the attempted checks and the real
  blocker. Do not mark the task complete by writing speculative documentation.

## Definition of done

For implementation work, completion normally requires:

1. A focused code, configuration, or test change that addresses the request.
2. Targeted validation actually executed for the affected module.
3. Broader regression checks only when shared boundaries, security, schemas,
   public APIs, or core helpers are affected.
4. A concise final report with commands and honest pass/fail/blocked results.

Markdown is supporting work, not the primary deliverable. Update existing
documentation only when the change affects a public API, schema/migration,
configuration, installation, operator workflow, architecture contract, or
user-visible behavior. Small internal fixes do not require a new `.md` file.

## Repository architecture

Preserve the canonical request path:

`Console -> Gateway -> Control -> Runtime Daemon`

- `console/` calls the Gateway public API; it must not call Control, Runtime, or
  data stores directly.
- `gateway/` is the transport/auth boundary and must not own domain persistence.
- `control/` owns orchestration and decisions; host execution stays behind the
  Runtime client boundary.
- `runtime-daemon/` owns execution, sandboxing, and capability enforcement.
- Use `docs/adr/0001-canonical-aion-ownership.md` and
  `docs/migration/canonical-paths.md` as the current ownership contract.
- Treat legacy roots as compatibility inputs until their documented retirement
  gates pass. Do not infer deletion authority from a path search or roadmap.

Stay on the currently checked-out branch unless the user explicitly requests a
branch change. A status ledger applies only when the current task names that
workflow; it is not a general task queue.

## Safety and scope

- Never run `DROP`, `TRUNCATE`, destructive cleanup, production deployment, or
  data deletion without explicit human approval.
- Do not delete files, paths, compatibility layers, columns, tables, or records
  as part of ordinary fixes.
- Do not change auth/permission systems, public APIs, schemas, financial logic,
  or production service topology unless the user explicitly places that change
  in scope.
- Do not switch branches, commit, push, merge, deploy, start persistent
  services, or install new dependencies unless requested or strictly necessary
  and justified.
- Never expose or persist secrets. Use placeholders in examples and tests.
- Rules about "agents" in `.codex/SECURITY.md` describe OMERTAOS runtime agents;
  they do not prohibit Codex from performing user-authorized engineering work
  within the repository and the active tool policy.

## Validation map

Start with the smallest relevant command:

- Python/Control/Data: `python -m pytest <affected-test-path> -q`
- Shared architecture smoke: `python -m pytest tests/architecture -q -k
  "not test_structure_migration_gate"`; run the intentionally red completion
  gate only when the current Structure phase explicitly targets that gate
- Gateway: `npm run build --prefix gateway` plus relevant Gateway tests
- Console: `npm run test --prefix console -- --config vitest.config.mts`; add a
  production build for routing, config, or shared UI changes
- Runtime: `cargo fmt --check` and targeted `cargo test` under
  `runtime-daemon/Cargo.toml`
- Compose: run `docker compose ... config` before any build; never run `up` or
  `down` unless the task explicitly requires a running stack
- CAPO shell assets on Windows: syntax/static checks only; do not claim native
  Linux/systemd validation without the intended host

Always inspect the exit code. A wrapper must not print success or exit zero
after an underlying test/lint command failed.

## Context efficiency and final report

- Start with focused `rg`/file reads and expand only through real dependencies.
- Preserve unrelated user changes in a dirty worktree.
- Keep diffs small and reuse repository-native helpers and patterns.
- In the final answer, include the completed work, changed files, validation
  results, risk/security notes, migration/rollback notes when applicable, and a
  suggested PR title. Keep non-applicable sections to one line instead of
  generating a large template.
- Human review is required before merge or production use. Do not auto-merge or
  deploy.
