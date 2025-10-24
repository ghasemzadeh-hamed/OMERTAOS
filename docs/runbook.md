# AION-OS Runbook

## Local Development

1. Copy `.env.example` to `.env` and adjust credentials.
2. Start Postgres and Redis locally (or run `docker-compose up postgres redis`).
3. Control plane:
   ```bash
   cd control
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
4. Gateway:
   ```bash
   cd gateway
   npm install
   npm run dev
   ```
5. Execution plane:
   ```bash
   cd execution
   cargo run
   ```
6. Web console:
   ```bash
   cd web
   npm install
   npm run dev
   ```

## Docker Deployment

```bash
docker compose up --build
```

Services exposed:
- Gateway: http://localhost:8080
- Control: http://localhost:8000/docs
- Web console: http://localhost:3000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

## Database Migration & Seed

1. Run Prisma migrations (metadata store for web console):
   ```bash
   npx prisma migrate deploy
   npx ts-node prisma/seed.ts
   ```
2. Control plane auto-migrates SQLModel tables on startup.

## First Admin Account

- Prisma seed creates `admin@aion.local` with password `admin123`.
- Authenticate via the web console auth panel to obtain a JWT token stored in local storage.

## Testing

```bash
cd gateway && npm test
cd control && pytest
cd execution && cargo test
cd web && npm test
```

E2E UI tests:
```bash
cd web
npx playwright test
```

## Deployment Pipeline

- GitHub Actions workflow `.github/workflows/ci.yml` executes lint → unit tests → Rust build.
- Build container images with:
  ```bash
  docker build -t aion-gateway ./gateway
  docker build -t aion-control ./control
  docker build -t aion-execution ./execution
  docker build -t aion-web ./web
  ```
- Publish to registry, then use the NixOS flake under `runtime/` to assemble a bootable runtime image with containerd orchestrating the containers.
