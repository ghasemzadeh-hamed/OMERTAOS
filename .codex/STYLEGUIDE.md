# OMERTAOS Style Guide

## General

- Prefer explicit, boring, maintainable code.
- Keep service boundaries clear.
- Do not hide business or runtime behavior in UI components.
- Keep comments focused on why, not what.

## TypeScript / Console / Gateway

- Use TypeScript types.
- Keep API clients in lib or service layers.
- Keep UI components separate from API orchestration.
- Gateway routes must stay focused on boundary, auth, proxying, validation, and transport concerns.

## Python / Control

- Prefer FastAPI routers/services/repositories.
- Keep Control business logic out of Gateway.
- Keep runtime execution calls behind explicit clients/adapters.
- Use structured errors and avoid raw exception leaks.

## Rust / Runtime

- Runtime should remain the execution boundary.
- Security, capability checks, audit, and sandbox behavior are critical.
- Avoid unsafe execution paths without explicit policy.

## Naming

- Python files: snake_case
- TypeScript components: PascalCase
- TypeScript functions: camelCase
- Database tables: plural snake_case
- API routes: /v1/resource/action where appropriate
- Model and agent IDs: stable, explicit, version-aware

## Error Handling

User-facing errors:
- Clear
- Non-technical
- Actionable

Internal logs:
- Structured
- Context-rich
- No secrets

## Documentation

Update an existing relevant document when setup, Docker, runtime, architecture,
public API, schema/migration, or operator behavior changes. An internal fix does
not automatically require a new Markdown file, and documentation must never
replace requested implementation.

When documentation is applicable, include:
- Purpose
- Files changed
- Commands to validate
- Known limitations
- Rollback notes when relevant
