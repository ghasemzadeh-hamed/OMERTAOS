#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# 0) .env اولیه
if [ ! -f ".env" ]; then
  cp .env.example .env || true
fi

# 1) فایل YAML کانفیگ Quick-Start
mkdir -p config
if [ ! -f "config/aionos.config.yaml" ]; then
  cat > config/aionos.config.yaml <<'YAML'
version: 1
onboardingComplete: false

admin:
  email: "admin@example.com"
  password: ""

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
    engine: "ollama"
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
YAML
fi

export AIONOS_CONFIG_PATH="${AIONOS_CONFIG_PATH:-$ROOT_DIR/config/aionos.config.yaml}"

# 2) بالا آوردن سرویس‌های اصلی
if command -v docker >/dev/null 2>&1; then
  docker compose up -d --build
fi

# 3) نصب LLM لوکال (Ollama - CPU/GPU خودکار)
chmod +x scripts/install_local_llm.sh scripts/install_vllm_gpu.sh scripts/smoke_e2e.sh
export AIONOS_LOCAL_MODEL="${AIONOS_LOCAL_MODEL:-llama3.2:3b}"
scripts/install_local_llm.sh "$AIONOS_LOCAL_MODEL"

# 4) تولید توکن ایجنت
AGENT_TOKEN=$(head -c 32 /dev/urandom | xxd -p)
if ! grep -q "^AGENT_API_TOKEN=" .env; then
  echo "AGENT_API_TOKEN=$AGENT_TOKEN" >> .env
fi
export AGENT_API_TOKEN="$(grep ^AGENT_API_TOKEN .env | tail -n1 | cut -d= -f2)"

# 5) انتظار برای آماده‌شدن کنسول
echo "Waiting for console (http://localhost:3000) ..."
for i in {1..90}; do
  if command -v curl >/dev/null 2>&1 && curl -fsS http://localhost:3000/ >/dev/null; then
    break
  fi
  sleep 2
done

# 6) بازکردن مرورگر
URL="http://localhost:3000"
if command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL" || true; fi
if command -v open >/dev/null 2>&1; then open "$URL" || true; fi

cat <<MSG
✅ Quick-Start آماده است.
• کنسول: $URL
• LLM محلی (Ollama): http://127.0.0.1:11434
• Agent Token ذخیره‌شده در .env → AGENT_API_TOKEN=$AGENT_API_TOKEN

برای استفاده از vLLM (GPU)، این را اجرا کن:
  docker compose -f docker-compose.yml -f docker-compose.vllm.yml up -d --build
MSG
