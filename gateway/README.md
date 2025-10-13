# AgentOS Gateway

This Node.js service terminates REST and WebSocket connections before forwarding them to the FastAPI control plane. It provides clustering, streaming passthrough, and request logging.

## Running locally

```bash
cd gateway
npm install
CORE_URL=http://localhost:8000 npm start
```

Set `GATEWAY_WORKERS` to override the number of worker processes.
