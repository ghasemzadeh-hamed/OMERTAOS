# API Reference

## REST

### GET /api/rest/tasks
- **Description:** Returns the list of tasks (RBAC: authenticated users).
- **Rate Limit:** 120 requests / 60 seconds.
- **Response:** `Task[]` including `project` and `assignee` relations.

### POST /api/rest/tasks
- **Description:** Creates a task (RBAC: admin).
- **Rate Limit:** 120 requests / 60 seconds per user.
- **Body:**
```json
{
  "title": "string",
  "description": "string",
  "projectId": "string",
  "assigneeId": "string"
}
```
- **Response:** `Task`

### POST /api/webhook
- **Description:** Broadcasts task updates to connected clients.
- **Body:** JSON payload forwarded to subscribers.

## tRPC

### project.list
- **Type:** Query
- **Returns:** Project[] with Task[]

### project.create
- **Type:** Mutation
- **Input:** `{ name: string; description?: string }`

### task.list
- **Type:** Query
- **Input:** `{ projectId?: string; query?: string }`

### task.create
- **Type:** Mutation
- **Input:** `{ projectId: string; title: string; description?: string; assigneeId?: string }`

### activity.feed
- **Type:** Query
- **Returns:** `ActivityLog[]`
