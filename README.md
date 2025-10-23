# AION-OS

AION-OS is a modular AI operating platform composed of a TypeScript gateway, FastAPI control plane, Rust execution modules, and a Next.js glassmorphism console.

## Getting Started

```bash
cp .env.example .env
pnpm install --prefix gateway
pnpm install --prefix web
python -m venv .venv && source .venv/bin/activate && pip install -r control/requirements.txt
```

To run all services locally:

```bash
docker compose up --build
```

Run individual services during development:

```bash
# Gateway
cd gateway && pnpm dev

# Control plane
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Execution modules
cd execution && cargo run

# Web console
cd web && pnpm dev
```

## Testing

```bash
cd gateway && pnpm test
cd control && pytest
cd web && pnpm test
cd execution && cargo test
```
