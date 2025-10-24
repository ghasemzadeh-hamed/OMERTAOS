# Performance Notes

- **Caching**: Gateway caches hot task lists in Redis; control plane may populate caches via `ActivityLog` watchers.
- **Async IO**: FastAPI routes use async SQLModel sessions and `httpx.AsyncClient` for external LLM calls.
- **Streaming**: SSE/WebSocket endpoints push live task updates with backpressure via Redis pub/sub.
- **Batching**: Execution plane ready for batched requests by extending the proto to include repeated payloads.
- **Next.js**: Client components rely on TanStack Query caching, and pages can adopt Incremental Static Regeneration by exporting `generateStaticParams` for read-most views.
- **Database**: Indexes defined on `Task.external_id` and `User.email` accelerate lookups.
- **Observability**: Prometheus histograms measure request latency enabling adaptive throttling.
