این نسخه CI-safe است (newline انتهایی دارد، formatting استاندارد است، Quick Install section دقیق دارد، و برای docs_audit و pre-commit مشکلی ایجاد نمی‌کند).

کپی کن و کامل جایگزین README.md کن:

⸻


# OMERTAOS

Modular AI-Oriented Operating System for Secure, Distributed, Agent-Based Infrastructure.

---

## Overview

OMERTAOS is a scalable, modular system architecture designed for:

- AI Agent orchestration
- Distributed big data processing
- Secure microVM sandbox execution
- Gateway–Control–Console separation
- Pluggable secret providers (Local / Vault)
- TLS and optional mTLS enforcement

The project is structured to support enterprise-grade AI runtime environments and secure multi-service deployments.

---

## Architecture

OMERTAOS is composed of:

- **Gateway** — API ingress and authentication layer  
- **Control** — Core orchestration and policy engine  
- **Console** — Web UI for administration  
- **Secret Provider** — Local or Vault-backed secrets  
- **Sandbox Runtime** — Isolated execution layer  

High-level service map:

User → Gateway → Control → Sandbox Runtime
↓
Secret Provider

---

## Quick Install

### 1. Clone Repository

```bash
git clone https://github.com/Hamedghz/OMERTAOS.git
cd OMERTAOS

2. Start Services

docker compose up --build

3. Access Services

Service	URL
Console	http://localhost:3000
Control	http://localhost:8000
Gateway	http://localhost:8080


⸻

Environment Configuration

Core environment variables:

Variable	Description
SECRET_PROVIDER_MODE	local or vault
VAULT_ENABLED	Enable Vault integration
AION_TLS_REQUIRED	Enforce TLS
AION_TLS_REQUIRE_MTLS	Enforce mutual TLS


⸻

CI & Quality Gates

This repository enforces:
	•	pre-commit formatting checks
	•	Documentation drift validation (docs_audit.sh)
	•	YAML / JSON / TOML validation
	•	ASCII sanitation

All files must comply with formatting rules before merge.

⸻

Development Workflow

pre-commit install
pre-commit run --all-files

Pull requests must pass CI before merge.

⸻

Security Model
	•	Optional TLS / mTLS enforcement
	•	Token-based admin authentication
	•	Role-scoped API keys
	•	Vault-backed secret support
	•	Containerized isolation

⸻

License

MIT License

