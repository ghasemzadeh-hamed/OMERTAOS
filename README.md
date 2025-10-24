# AION-OS Big Data Edition

This repository provisions the streaming, analytics, and reinforcement learning loop for the AION-OS decision router.

## Getting Started
1. Copy `.env.bigdata.example` to `.env.bigdata` and update secrets.
2. `docker compose -f docker-compose.yml -f docker-compose.bigdata.yml up -d`
3. Run `pytest` to validate schema contracts and policy management.
4. Trigger `bigdata/scripts/smoke_test.sh` to send a sample router decision through the pipeline.

See [`docs/bigdata.md`](docs/bigdata.md) for detailed architecture and operations guidance.
