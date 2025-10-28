#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# 1) .env اولیه
if [ ! -f ".env" ]; then
  cp .env.example .env || true
fi

# 2) فایل YAML کانفیگ راه‌انداز
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
  provider: "openai"
  openaiApiKey: ""
  defaultModel: "gpt-4o-mini"
security:
  enableMTLS: false
  allowRegistrations: false
telemetry:
  otelEnabled: true
  serviceName: "aionos"
YAML
fi

# 3) بالا آوردن سرویس‌ها (Docker)
if command -v docker >/dev/null 2>&1; then
  docker compose up -d --build
fi

# 4) انتظار برای آماده‌شدن کنسول
echo "Waiting for console (http://localhost:3000) ..."
for i in {1..90}; do
  if command -v curl >/dev/null 2>&1 && curl -fsS http://localhost:3000/ >/dev/null; then
    break
  fi
  sleep 2
done

# 5) باز کردن مرورگر
URL="http://localhost:3000"
if command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL" || true; fi
if command -v open >/dev/null 2>&1; then open "$URL" || true; fi

echo "✅ نصب اولیه تمام شد. مرورگر را در $URL باز کنید."
