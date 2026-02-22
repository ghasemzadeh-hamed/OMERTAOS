# OMERTAOS

Modular AI-Oriented Operating System for Secure Distributed Agent Infrastructure.

---

## Overview

OMERTAOS is a scalable modular architecture designed for:

- AI agent orchestration
- Distributed processing
- Secure sandbox execution
- Gateway Control Console separation
- Pluggable secret providers
- Optional TLS and mTLS enforcement

---

## Architecture

Core components:

- Gateway
- Control
- Console
- Secret Provider
- Sandbox Runtime

Flow:

User -> Gateway -> Control -> Sandbox

---

## Quick Install

Clone the repository:

git clone https://github.com/Hamedghz/OMERTAOS.git
cd OMERTAOS

Start services:

docker compose up --build

Access:

Console  http://localhost:3000  
Control  http://localhost:8000  
Gateway  http://localhost:8080  

---

## Environment Variables

SECRET_PROVIDER_MODE  
VAULT_ENABLED  
AION_TLS_REQUIRED  
AION_TLS_REQUIRE_MTLS  

---

## CI Enforcement

This repository enforces:

- pre-commit hooks
- documentation audit
- yaml json toml validation
- ascii sanitation

All commits must pass CI before merge.

---

## License

MIT