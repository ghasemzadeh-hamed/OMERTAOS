# OMERTAOS

AI-Oriented Modular Operating System Infrastructure  
Secure • Distributed • Agent-Driven • Scalable

---

## Overview

OMERTAOS is a modular, distributed infrastructure platform designed to orchestrate AI agents, secure services, and scalable runtime environments.

The system separates responsibilities into isolated layers:

- **Gateway** – External API access and authentication layer  
- **Control** – Core orchestration and agent management engine  
- **Console** – Web-based UI for monitoring and administration  
- **Secret Provider** – Local or Vault-backed secret management  
- **MicroVM Runtime (optional)** – Sandboxed AI execution layer  

---

## Architecture Principles

- Modular service separation
- Secure-by-default configuration
- Agent-oriented orchestration
- Environment-based deployment modes
- CI-enforced documentation integrity

---

## Repository Structure

/gateway        → API layer
/control        → Core orchestration
/console        → Frontend UI
/scripts        → CI / utility scripts
/docker         → Container definitions

---

## Quick Install

### 1. Clone the Repository

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

Key variables:
	•	VAULT_ENABLED
	•	SECRET_PROVIDER_MODE
	•	AION_TLS_REQUIRED
	•	NEXTAUTH_SECRET
	•	AION_ADMIN_TOKEN

Deployment modes:
	•	Local (default)
	•	Vault-backed secrets
	•	TLS / mTLS secured

⸻

CI & Quality Enforcement

This repository enforces:
	•	Pre-commit formatting rules
	•	End-of-file normalization
	•	Documentation drift checks
	•	YAML / JSON / TOML validation

All commits must pass automated checks.

⸻

Security Model
	•	Token-based admin authentication
	•	Optional mTLS enforcement
	•	Segmented service architecture
	•	Isolated runtime execution layer

⸻

Roadmap
	•	MicroVM sandbox stabilization
	•	Agent workflow engine expansion
	•	Distributed cluster mode
	•	Enterprise secret rotation support

⸻

License

MIT License

⸻

Maintained by Hamed Ghasemzadeh.
 
	