# API Documentation

## Gateway REST

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Gateway health check |
| `POST` | `/auth/login` | Obtain JWT token |
| `GET` | `/tasks` | Proxy task listing from control plane |
| `POST` | `/tasks` | Create task routed via control plane |
| `GET` | `/tasks/{id}` | Fetch single task |
| `POST` | `/tasks/{id}/cancel` | Cancel running task |
| `GET` | `/events/tasks?token=` | SSE stream of task updates |
| `GET` | `/stream/tasks` | WebSocket stream of task updates |

## Control Plane REST

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/login` | Exchange credentials for JWT |
| `POST` | `/users` | Create user (admin only) |
| `GET` | `/tasks` | List tasks |
| `POST` | `/tasks` | Enqueue task and trigger AI router |
| `GET` | `/tasks/{id}` | Task details |
| `POST` | `/tasks/{id}/cancel` | Cancel task |
| `POST` | `/agents/manifest` | Register agent manifest |
| `GET` | `/metrics` | Prometheus metrics |

## gRPC Service

```proto
service TaskExecutor {
  rpc ExecuteTask(TaskRequest) returns (TaskResponse);
}

message TaskRequest {
  string external_id = 1;
  string intent = 2;
  string payload = 3; // JSON blob
}

message TaskResponse {
  string external_id = 1;
  string status = 2;
  string output = 3; // JSON blob
}
```

## tRPC

A lightweight tRPC router can be added by extending the FastAPI control plane with `fastapi-trpc`. Current architecture exposes REST/GraphQL friendly JSON endpoints.
