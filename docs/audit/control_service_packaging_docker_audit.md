# Control Service Packaging & Docker Structural Audit

## Scope
This audit reviews packaging, imports, monorepo layout, Docker image construction, and CI behavior for the control service startup path (`python -m control.os.main`).

## 1) Package Structure Validation

### Observed state
- `control/` is a Python package (contains `control/__init__.py`) and has its own `pyproject.toml`.
- `shared/`, `kernel/`, `secret_store/`, and `config/` each contain `__init__.py` at their roots.
- `policies/` does **not** contain `__init__.py` and is currently a data/config directory, not a Python package.
- `control/os/config.py` imports `secret_store`, and `secret_store/__init__.py` re-exports from `shared.secret_store`.

### Critical finding: why `ModuleNotFoundError: No module named 'shared'` occurs
The control Dockerfile copies `secret_store` but does **not** copy `shared` into the image. Therefore, import resolution chain breaks:

1. `control.os.config` imports `secret_store`
2. `secret_store` imports `shared.secret_store`
3. `shared/` is absent in the image filesystem
4. Python raises `ModuleNotFoundError: No module named 'shared'`

This is first a **missing folder in image** issue.

### Secondary packaging findings
- `control/pyproject.toml` package discovery is misconfigured:
  - `[tool.setuptools.packages.find] include = ["os*", "aion_control*"]`
  - It does **not** include `control*`.
- As written, editable install can register wrong packages (including top-level `os`) and omit intended `control` package metadata.
- Runtime currently succeeds mostly because `PYTHONPATH=/srv/app` exposes copied source directly, masking packaging defects.

## 2) Monorepo Design Review

### Classification
Current repo is an **improper hybrid monorepo**:
- Some components behave as standalone packages (`control` has `pyproject.toml`).
- Some are importable modules but unmanaged as packages (`shared`, `kernel`, `secret_store`, `config`).
- Some are data-only (`policies`) but copied beside code.

### Recommended architecture
For this system, **Option A (proper multi-package monorepo)** is superior:

```
/srv/app
  control/        # pyproject.toml
  shared/         # pyproject.toml
  kernel/         # pyproject.toml (if imported as Python)
  secret_store/   # either package or folded into shared
  config/         # keep as data module only if intentionally importable
  policies/       # data/policy assets; not a Python package unless needed
```

Why Option A:
- Clear dependency contracts between services/modules.
- Independent versioning and wheel building.
- Fewer import side effects from raw `PYTHONPATH` hacks.
- Better CI reproducibility.

Option B (`src/` single-root package) is also valid for one deployable unit, but this codebase already shows service boundaries and shared libraries, so multi-package is cleaner operationally.

## 3) Dockerfile Architecture Review

### Current Dockerfile issues
- Missing `COPY shared ./shared` (root-cause breaker).
- Partial copy set risks future hidden import failures.
- `pip install -e ./control` in production is not ideal (editable installs are dev-oriented and less deterministic).
- Package install is not aligned to actual inter-package dependencies.
- Build caching can be improved by separating dependency metadata from source copies.

### Production-grade rewrite (single-image, pip)

```dockerfile
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

# 1) Copy package metadata first for cache-friendly dependency resolution
COPY control/pyproject.toml control/README.md ./control/
# If/when shared/kernel become installable packages, copy their pyproject files too.

# 2) Copy runtime source tree
COPY control ./control
COPY shared ./shared
COPY secret_store ./secret_store
COPY kernel ./kernel
COPY config ./config
COPY policies ./policies

# 3) Install non-editable for deterministic runtime behavior
RUN pip install --upgrade pip setuptools wheel \
 && pip install ./control

# Optional: run as non-root
RUN useradd -m -u 10001 appuser
USER appuser

EXPOSE 8000

CMD ["python", "-m", "control.os.main"]
```

## 4) PYTHONPATH & Import System Analysis

- Python resolves imports from `sys.path` in order (current working dir, stdlib, site-packages, `PYTHONPATH`, etc.).
- `python -m control.os.main` executes module as part of package context, so absolute imports like `from control.os.config import ...` are correct.
- Relative imports are acceptable only internally; across service boundaries use explicit absolute package imports.

### Stable import strategy
- Do **not** rely on broad `PYTHONPATH=/srv/app` as primary integration mechanism.
- Prefer installable packages and explicit dependencies.
- Keep absolute imports (`control.*`, `shared.*`) and avoid ambiguous top-level names (`os`).

## 5) CI/CD Root Cause Analysis

Why local may pass while GitHub Actions fails:
- Local docker-compose often bind-mounts repo root, making `shared/` visible even if image lacks it.
- CI typically runs clean image build + container run without host mounts.
- Editable installs in local/dev can mask broken package metadata due source availability.
- Clean CI environments expose missing COPY and packaging misconfigurations immediately.

## 6) Production Hardening Recommendations

1. **Security**
   - Run as non-root user.
   - Pin base image digest.
   - Reduce OS packages to runtime minimum.
2. **Image size/perf**
   - Use multi-stage build (build wheels in builder, install wheels in runtime).
   - Remove build tools from runtime stage.
3. **Determinism**
   - Use lockfile/constraints (`requirements.lock` or `pip-tools`).
   - Avoid editable installs in production.
4. **Health/ops**
   - Add `HEALTHCHECK` against `/health` endpoint.
   - Set explicit timeouts and graceful shutdown settings.
5. **Packaging**
   - Fix `control` package discovery to `include = ["control*", "aion_control*"]`.
   - Convert `shared` to a first-class package with its own `pyproject.toml`.
   - Keep `policies/` as data assets unless executable policy code is intended.

## 7) Final Deliverable Summary

### Root cause
Primary: Docker image omits `shared/` while runtime imports require `shared.secret_store` through `secret_store` shim.

### Structural redesign plan
- Promote shared libraries to installable packages.
- Eliminate production editable installs.
- Remove implicit dependency on repository-root `PYTHONPATH`.

### Correct folder strategy
- Adopt multi-package monorepo with explicit package boundaries and per-package metadata.

### Correct packaging strategy
- Fix `control` setuptools include to `control*`.
- Add package metadata for `shared` (and others if imported).

### Correct import strategy
- Absolute imports across packages; limited relative imports within package internals.

### CI-safe configuration
- Build/test in clean images without host mounts.
- Run smoke import checks in CI (e.g., `python -c "import control, shared, secret_store"`).
