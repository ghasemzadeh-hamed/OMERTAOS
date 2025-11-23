# APIs & Contracts Review

## 1. Services and Endpoints Catalog
- **Gateway (Fastify)**
  - `/health`, `/healthz`: liveness endpoints.
  - `/api/dev/kernel` (POST): proxy to dev kernel for test payloads when enabled.
  - `/v1/tasks` (POST): submit task to control plane (gRPC) with idempotency and routing metadata enrichment.
  - `/v1/tasks/:id` (GET): fetch task status/result by id.
  - `/v1/stream/:id` (GET SSE) and `/v1/ws` (WebSocket): stream task updates.
  - `/v1/config/*`: admin-only proxy to control config APIs (`propose`, `apply`, `revert`, `status`, `profile`).
  - `/v1/models` (GET): list models from control, falling back to profile defaults.
  - `/v1/seal/*` (conditional): admin-only proxy to SEAL job and router policy endpoints.
- **Control / Plugin Registry (FastAPI)**
  - `/plugins/` (GET): list available plugins.
  - `/plugins/call` (POST): invoke a plugin with parameters.
  - `/healthz` (GET): readiness probe.
- **Catalog API (FastAPI)**
  - `/catalog` (GET): list tools with optional category/query filters.
  - `/catalog/upsert` (POST): create/update tool and category metadata.
  - `/catalog/{name}/install` (POST): trigger install job for a tool.
  - `/catalog/{name}/config` (GET/POST): read/write per-environment config via vault.
- **Model Registry (FastAPI)**
  - `/models` (POST/GET): register model and list models ordered by score.
  - `/routes` (POST) & `/routes/{agent_id}` (GET): manage model routing per agent.
- **Memory Service (FastAPI)**
  - `/interactions` (POST/GET by id): create and retrieve interaction records with linked self-edits.
  - `/self-edits` (POST): create self-edit for an interaction.
  - `/self-edits/top` (GET): list top self-edits filtered by reward and limit.
- **SEAL Adapter (FastAPI)**
  - `/run` (POST): executes one SEAL iteration.
- **gRPC Tasks Service (`aion.v1.AionTasks`)**
  - `Submit`, `Stream`, `AckStream`, `StatusById` methods for task lifecycle.

## 2. Endpoint Specifications
### Gateway
- **POST `/v1/tasks`**
  - Schema: `TaskRequest` with fields `schemaVersion`, `intent`, optional `params`, `preferredEngine`, `priority`, optional `sla` (`budget_usd`, `p95_ms`, `privacy`), and optional `metadata`.
  - Response: `TaskResult` (`schemaVersion`, `taskId`, `intent`, `status`, `engine` decision, optional `result`, `usage`, `error`).
  - Status: `200` on success; `400` for validation errors; `401/403` for auth failures; `404` if downstream task missing; `503` for dev kernel or idempotency cache failures.
  - Errors: validation issues returned as list of `path/message/code`; custom `GatewayError` payload with `statusCode` for unhandled errors.
  - Versioning: path includes `v1`; payload carries `schemaVersion`.
  - Rate limiting: global request hook (`rateLimitMiddleware`) plus idempotency via `Idempotency-Key` header with cache persistence.
  - Auth: pre-handler enforces roles `user/manager/admin` via API key or JWT; tenant derived from headers or token.
- **GET `/v1/tasks/:id`**
  - Path param: `id` (taskId).
  - Response: `TaskResult` or `404` if not found.
- **GET `/v1/stream/:id` (SSE) & `/v1/ws` (WebSocket)**
  - Streams `TaskResult` updates; SSE uses `id` param, WS uses `subscribe` action with `taskId` and heartbeat messages.
- **POST `/api/dev/kernel`**
  - Schema: `DevKernelRequest` with `message` and optional `metadata`.
  - Response: proxy `DevKernelResponse { type, content }`; `503` if disabled/unavailable.
- **Config Proxy (`/v1/config/*`)**
  - Admin-only; forwards to control service with bearer token header when configured.
  - `POST /v1/config/propose` (body forwarded), `/apply`, `/revert`; `GET /status`, `/profile`; `POST /profile` to set profile payload.
- **Models Proxy (`/v1/models`)**
  - `GET`: returns control list or fallback stub.
- **SEAL Proxy (`/v1/seal/*`)**
  - Enabled when feature flag true; admin-only forwarding to `/v1/seal/jobs`, `/v1/seal/jobs/{id}/status`, `/v1/seal/streams/{id}`, `/v1/router/policy/reload`.

### Control / Plugin Registry
- **GET `/plugins/`**: returns `{ available: [plugin_names...] }`.
- **POST `/plugins/call`**
  - Body: `{ name: string, params?: object }`.
  - Responses: plugin output; `400` if name blank or bad params; `404` if unknown; `424` if missing extras; `200` with note when module lacks `aion_entry`.
- **GET `/healthz`**: `{ status: "ok" }` for readiness.

### Catalog API
- **GET `/catalog`**
  - Query: `category`, `q`.
  - Response: `{ items: [tool summary...] }` with category/title, tags, docs/repo, config schema.
- **POST `/catalog/upsert`**
  - Body: `{ category: string, tool: {...} }` supporting name, display_name, version, tags, URLs, config_schema.
  - Response: `{ ok: true, tool: {...} }` after insert/update.
- **POST `/catalog/{name}/install`**
  - Body: `{ env?, version?, editable?, repo_url? }`.
  - Response: `{ status, log?, installation: {...} }`; `404` if tool missing; `403` if editable denied.
- **POST `/catalog/{name}/config`** and **GET `/catalog/{name}/config`**
  - Stores/reads config in vault under `aion/{env}/{name}`; require `vault.write` / `vault.read` permissions.

### Model Registry
- **POST `/models`**
  - Body: `{ name, parent?, path, score, metadata? }`.
  - Response: stored model with `active` flag and timestamps; `400` if name exists.
- **GET `/models`**: list ordered by score desc.
- **POST `/routes`**
  - Body: `{ agent_id, model_name }`; requires model active else `404`; returns `{ status: "ok" }`.
- **GET `/routes/{agent_id}`**: returns mapping or `404` if missing.

### Memory Service
- **POST `/interactions`**
  - Body: `{ agent_id, user_id?, model_version, input_text, output_text, channel? }`.
  - Response: persisted interaction with id/timestamp.
- **GET `/interactions/{interaction_id}`**: returns interaction plus `self_edits`; `404` if not found.
- **POST `/self-edits`**
  - Body: `{ interaction_id, original_output, edited_output, reason?, reward }`; `404` if interaction missing.
  - Response: stored self-edit.
- **GET `/self-edits/top`**
  - Query: `min_reward` (default 0.7), `limit` (default 256).
  - Response: list of top self-edits ordered by reward then recency.

### SEAL Adapter
- **POST `/run`**: executes one SEAL iteration; response from `run_seal_iteration()` payload.

### gRPC Tasks (Control Plane)
- **Submit(TaskRequest) → TaskResult**: enqueue/execute task.
- **Stream(TaskRequest) → stream StreamChunk**: streaming task results with control metadata.
- **AckStream(StreamAck) → AckResponse**: consumer acknowledgements.
- **StatusById(TaskId) → TaskResult**: fetch task state by id.

## 3. Examples
- **Submit task (HTTP)**
  ```bash
  curl -X POST https://gateway.example.com/v1/tasks \
    -H "Authorization: Bearer <jwt>" \
    -H "Idempotency-Key: 123e4567" \
    -H "Content-Type: application/json" \
    -d '{
      "intent": "summarize",
      "params": {"text": "hello world"},
      "preferredEngine": "auto",
      "metadata": {"agent_id": "agent-42"}
    }'
  ```
  **Response**
  ```json
  {
    "schemaVersion": "1.0",
    "taskId": "<uuid>",
    "intent": "summarize",
    "status": "PENDING",
    "engine": {"route": "auto", "chosen_by": "gateway", "reason": "initial submit"}
  }
  ```
- **Get task result**
  ```bash
  curl -H "Authorization: Bearer <jwt>" https://gateway.example.com/v1/tasks/<taskId>
  ```
- **Subscribe via SSE**
  ```bash
  curl -N -H "Authorization: Bearer <jwt>" https://gateway.example.com/v1/stream/<taskId>
  ```
- **Catalog upsert**
  ```bash
  curl -X POST http://localhost:8000/catalog/upsert \
    -H "x-role: admin" -H "Content-Type: application/json" \
    -d '{"category": "retrieval", "tool": {"name": "my-rag", "latest_version": "0.1.0", "tags": ["rag"]}}'
  ```
- **Model register**
  ```bash
  curl -X POST http://localhost:8001/models \
    -H "Content-Type: application/json" \
    -d '{"name": "llama3", "path": "s3://models/llama3", "score": 0.92}'
  ```
- **Memory self-edit**
  ```bash
  curl -X POST http://localhost:8002/self-edits \
    -H "Content-Type: application/json" \
    -d '{"interaction_id": 1, "original_output": "hi", "edited_output": "hello", "reward": 0.9}'
  ```

## 4. Contract Governance & Policy
- **Ownership**: Gateway contracts owned by API platform team; control/catalog/model/memory services owned by respective service leads.
- **Approval**: Breaking changes require design review and ADR update; minor additive changes follow change request with backward compatibility validation.
- **Versioning**: URI versioning (`/v1/...`) for HTTP; `schemaVersion` field in payloads; gRPC uses package version `aion.v1`. New versions released in parallel with deprecation windows communicated in release notes.
- **Documentation**: FastAPI auto-docs (OpenAPI), gRPC `.proto` source (`protos/aion/v1/tasks.proto`), gateway contract summarized here; publish artifacts to internal portal and registry.
- **Change notification**: Release notes and developer mailing list; breaking changes flagged 2 cycles ahead with migration guides; sunset dates recorded in ADRs.

## 5. Additional Considerations
- **Async/Streaming**: Gateway exposes SSE and WebSocket streaming; gRPC `Stream` supports bidirectional flow with ack markers; SEAL streams proxied via gateway when feature enabled.
- **Common policies**: Auth via API key or RS256 JWT with role enforcement; tenant resolution from headers; correlation and request IDs set on every response; CORS configurable; rate limiting middleware; idempotency cache for task submissions.
- **Security**: Admin routes gated by role; bearer propagation to control proxies; TLS assumed at ingress; sensitive configs stored in vault (catalog config endpoints).
- **Constraints**: JSON payloads only; request schemas validated (Zod/Pydantic); max payload sizes governed by Fastify defaults; dev kernel endpoints disabled unless feature flag set; catalog installs may require specific roles for editable installs.
- **Inter-service deps**: Gateway proxies to control plane via gRPC and HTTP; model routing resolves via model registry; memory logging invoked post-task for self-evolving features.
