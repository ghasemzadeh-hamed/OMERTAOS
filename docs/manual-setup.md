# Manual Setup Guide

This guide walks through configuring AION-OS without the helper scripts. It covers prerequisites, configuration, container orchestration, and optional overlays so you can deploy the stack on any development or staging machine.

---

## 1. Prerequisites
- **Docker** and **Docker Compose** (Compose v2). For Linux with GPU workloads, install the NVIDIA driver and NVIDIA Container Toolkit.
- **Git** for cloning the repository.
- **curl** or **HTTPie** for smoke testing.
- **Make** (optional) for convenience targets.
- Open outbound network access to fetch container images from Docker Hub and GitHub Container Registry.

### Recommended host resources
- CPU: 8 cores or more.
- Memory: 16 GB RAM.
- Storage: 20 GB free disk space for containers, volumes, and models.
- GPU (optional): NVIDIA GPU with at least 8 GB VRAM for vLLM workloads.

---

## 2. Clone the Repository
```bash
git clone -b AIONOS --single-branch https://github.com/ghasemzadeh-hamed/OMERTAOS.git
cd OMERTAOS
```

---

## 3. Prepare Environment Files
Create `.env` files for the root project, console, and control plane. Copy the examples and adjust values to match your environment.

```bash
cp config/templates/.env.example .env
cp console/.env.example console/.env
cp control/.env.example control/.env
```

Minimum values to review:
- `console/.env`: database DSN, Redis URL, seed admin credentials, FastAPI base URL.
- `control/.env`: Postgres DSN, Redis URL, MinIO endpoint.
- Root `.env`: API keys, agent tokens, and optional feature flags.

> **Tip:** Store real secrets in Docker/K8s secret stores or encrypted with SOPS. Do not commit modified `.env` files.

---

## 4. Configure the Runtime (Optional)
If you need to customize the runtime (e.g., change local LLM defaults), edit `config/aionos.config.yaml`. If the file does not exist, create one based on the snippet below:

```yaml
version: 1
onboardingComplete: false

admin:
  email: "admin@localhost"
  password: "admin"

console:
  port: 3000
  baseUrl: "http://localhost:3000"
  locale: "fa"

gateway:
  port: 8080
  apiKey: ""

control:
  httpPort: 8000
  grpcPort: 50051

data:
  postgres: { host: "postgres", port: 5432, user: "aionos", password: "aionos", db: "aionos" }
  redis:    { host: "redis", port: 6379 }
  qdrant:   { host: "qdrant", port: 6333 }
  minio:    { endpoint: "http://minio:9000", accessKey: "minioadmin", secretKey: "minioadmin", bucket: "aionos" }

models:
  provider: "local"
  local:
    engine: "ollama"   # options: ollama, vllm
    model: "llama3.2:3b"
    ctx: 4096
    temperature: 0.2
    num_gpu: 0
  routing:
    mode: "local-first"
    budget_ms: 18000
    allow_remote: false

agent:
  enabled: true
  allow_ui_tool: false
  policy:
    allowed_paths:
      - "/api/*"
    allowed_ui_actions:
      - "click"
      - "fill"
      - "press"

security:
  agent_api_token: ""

telemetry:
  otelEnabled: true
  serviceName: "aionos"
```

Save the file and export the path if you store it elsewhere:
```bash
export AIONOS_CONFIG_PATH=/absolute/path/to/aionos.config.yaml
```

---

## 5. Launch Core Services
Start the base stack:
```bash
docker compose up -d --build
```

Wait for the containers to become healthy. Verify with `docker compose ps` and inspect logs if necessary:
```bash
docker compose logs -f gateway
```

### Optional overlays
- **Big Data pipeline**: `docker compose -f docker-compose.yml -f bigdata/docker-compose.bigdata.yml up -d`
- **Local GPU inference (vLLM)**: `docker compose -f docker-compose.yml -f docker-compose.vllm.yml up -d --build`

> Ensure the NVIDIA runtime is installed before enabling GPU workloads.

---

## 6. Seed Credentials & Tokens
1. Generate an admin API key and append it to `.env`:
   ```bash
   echo "AION_GATEWAY_API_KEYS=demo-key:admin|manager" >> .env
   ```
2. Create an agent token for UI flows:
   ```bash
   head -c 32 /dev/urandom | xxd -p >> agent_token.txt
   echo "AGENT_API_TOKEN=$(cat agent_token.txt)" >> .env
   ```
3. Restart the affected services if you change secrets:
   ```bash
   docker compose restart gateway control console
   ```

> **Console sign-in:** the default seed user is `admin` (email `admin@localhost`) with password `admin`.

---

## 7. Verify the Deployment
- Console UI: `http://localhost:3000`
- Gateway API: `http://localhost:8080`
- Control API docs: `http://localhost:8000/docs`
- Health checks: append `/healthz` to each service URL.

Run the smoke script for a quick validation:
```bash
./scripts/smoke_e2e.sh
```

Manual API check:
```bash
curl -X POST http://localhost:8080/v1/tasks \
  -H "X-API-Key: demo-key" \
  -H "Content-Type: application/json" \
  -d '{"schemaVersion":"1.0","intent":"summarize","params":{"text":"Hello AION-OS!"}}'
```

Stream events for the task:
```bash
curl -H "X-API-Key: demo-key" http://localhost:8080/v1/stream/<task_id>
```

---

## 8. Optional Workloads
### Knowledge & RAG
```bash
curl -F "col=aionos-docs" -F "files=@README.md" http://localhost:8000/rag/ingest
curl -X POST http://localhost:8000/rag/query \
  -H "content-type: application/json" \
  -d '{"collection":"aionos-docs","query":"What is AION-OS?","limit":3}'
```

### Agent Mode
Set `NEXT_PUBLIC_CONTROL_BASE` and `NEXT_PUBLIC_AGENT_API_TOKEN` in `console/.env`, then open `http://localhost:3000/agent`.

### Switching Model Providers
Edit `config/aionos.config.yaml` and toggle between `ollama` and `vllm`. Restart the affected services after changes:
```bash
docker compose restart console control gateway
```

---

## 9. Security Considerations
- Protect `/agent/*` and `/admin/onboarding/*` routes with authentication.
- Enable mTLS for inter-service gRPC in production deployments.
- Use Vault or SOPS to manage secrets under `policies/secrets/`.
- Verify Cosign signatures for module images before promotion.

---

## 10. Troubleshooting
| Symptom | Resolution |
| --- | --- |
| Gateway returns 429 | Verify Redis availability and rate limit configuration. |
| Task latency spike | Inspect Grafana Router dashboard and Kafka topic `aion.metrics.runtime`. |
| Module start failure | Check module host logs, verify Cosign signatures, and roll back the manifest. |
| Missing BigData overlay | Ensure `bigdata/docker-compose.bigdata.yml` exists before enabling the overlay. |

For additional operations guidance, see [`docs/runbook.md`](runbook.md).

