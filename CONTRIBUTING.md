# Contributing to aionOS (AIONOS)

First off, thank you for taking the time to contribute! This document explains how to set up your environment, coding standards, and the workflow we use.

## 1) Ground Rules
- Be kind and respectful (see `CODE_OF_CONDUCT.md`).
- Prefer small, focused PRs with clear scope.
- Write tests for new features and bug fixes.
- Avoid introducing breaking changes without discussion.

## 2) Developer Setup (native)
See `README.md` for system requirements.

```bash
# Gateway
cd gateway && npm ci && npm run dev

# Control
cd control && python3.11 -m venv .venv && source .venv/bin/activate
python -m pip install -U pip wheel && python -m pip install -e .[dev]
uvicorn os.control.main:app --host 0.0.0.0 --port 50052 --reload
```

Optional services: Redis/Postgres/Mongo/Qdrant/MinIO — enable only what your change needs.

3) Style & Linting
•TypeScript (gateway/console): ESLint + Prettier (npm run lint, npm run format).
•Python (control): Ruff/Black (ruff check ., black .), type hints encouraged (mypy if configured).
•Rust (modules): cargo fmt, cargo clippy.

4) Tests
•Unit: colocated with source where possible.
•Integration/E2E: tests/ (spin gateway+control; use in-memory or local services).
•CI runs tests and security scans (see .github/workflows).

5) Commit & Branching
•Conventional Commits (examples):
•feat(gateway): add SSE idempotency window
•fix(control): guard against empty params
•docs(readme): clarify native setup
•Branches: feature/<short-desc>, fix/<short-desc>, docs/<short-desc>.
•Reference issues with Fixes #123 or Refs #123 in the PR description.

6) Opening a PR
•Ensure npm test / pytest / cargo test (as applicable) pass locally.
•Update docs (README.md, policies/*.yml, examples) if behavior changes.
•Add/Update API schemas if endpoints change.
•Fill out the PR template (if present) and include:
•Motivation & Context
•Changes summary
•Testing strategy
•Screenshots or curl examples when relevant
•Mark as Draft if still exploring.

7) E2E Smoke (manual)

```
curl -X POST "http://localhost:8080/v1/tasks" \
  -H "Content-Type: application/json" -H "X-API-Key: dev-key" \
  -d '{"schemaVersion":"1.0","intent":"summarize","params":{"text":"Hello"}}'

curl -N "http://localhost:8080/v1/stream/<TASK_ID>" -H "X-API-Key: dev-key"
```

8) Security & Responsible Disclosure
•Never commit secrets or test tokens.
•Report vulnerabilities per SECURITY.md. Do not open public issues for security matters.

9) Governance

See GOVERNANCE.md (if present) for maintainers’ roles and decision process.

Thanks for helping make aionOS better!
