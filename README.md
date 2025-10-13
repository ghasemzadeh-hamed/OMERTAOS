# AgentOS REST Interface Prototype

This repository contains a three-tier reference implementation that wires together a Node.js gateway, FastAPI control plane, and Rust execution module. The system demonstrates the decision-routing pattern outlined in the design brief and provides working code that can be extended for production-grade deployments.

## Architecture Overview

```
┌──────────────────────────┐
│   Node.js Gateway Layer  │  ← REST & WebSocket ingress
└────────────┬─────────────┘
             │ REST/Stream
┌────────────┴────────────┐
│   FastAPI Control Core  │  ← AI router & orchestration
└────────────┬────────────┘
             │ subprocess/gRPC
┌────────────┴────────────┐
│     Rust Local Modules  │  ← High-performance tasks
└──────────────────────────┘
```

* **Gateway (`gateway/server.js`)** handles JSON REST requests and WebSocket clients. It clusters across CPU cores and proxies streaming responses from the control plane.
* **Control plane (`core/app/main.py`)** exposes `/dispatch` and `/stream` endpoints. Requests are scored by an asynchronous decision router before being delegated to the appropriate executor.
* **Rust module (`rust_modules/processor`)** consumes JSON via stdin and returns deterministic responses for summarization, preprocessing, or token counting workloads.

## Local Development

1. Start the Rust service (builds on demand when invoked by FastAPI):

   ```bash
   cd rust_modules/processor
   cargo build
   ```

2. Launch the FastAPI control plane:

   ```bash
   cd core
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. Boot the Node.js gateway:

   ```bash
   cd gateway
   npm install
   CORE_URL=http://localhost:8000 npm start
   ```

4. Send a sample request:

   ```bash
   curl -X POST http://localhost:3000/api/v1/requests \
     -H 'Content-Type: application/json' \
     -d '{"request_id":"demo-1","prompt":"Summarize this sample text.","task_type":"summarize"}'
   ```

The WebSocket endpoint is available at `ws://localhost:3000/ws` and streams JSON lines matching the `StreamChunk` schema.
