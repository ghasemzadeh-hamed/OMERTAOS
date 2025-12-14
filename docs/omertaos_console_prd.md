# OmertaOS Console - Power User UI (Agents, Runs, Tools, Policies, OS Chat)

## One-Page PRD (ASCII)

**Title**
OmertaOS Console - Power User UI (Agents, Runs, Tools, Policies, OS Chat)

**Problem**
Power users need a single console to build/configure agents, execute workflows, debug failures, control cost, and enforce governance (tools/memory/policies) with full traceability.

**Goals**
- G1. Fast path from config -> first successful run (minutes, not hours)
- G2. Full reproducibility: every run is explainable + replayable + diffable
- G3. Operational clarity: real-time status, logs, traces, artifacts, cost
- G4. Governance clarity: policy decisions and tool permissions are visible and enforceable
- G5. Admin-grade performance: handle large run volumes, fast filtering, bulk actions

**Non-goals (explicit)**
- N1. End-user consumer chat product
- N2. Full-feature incident management suite (integrate later)
- N3. Building new agent runtime logic in console (console is control plane)

**Primary personas**
- P1. Power Operator (Admin): config + debug + governance + cost control
- P2. Platform Engineer: integrations, tools, environments, secrets, observability

**Key user journeys**
- J1. Create agent from template -> connect secrets -> test -> publish -> run
- J2. Explore runs -> filter failed -> open run detail -> root cause -> replay/fork -> compare
- J3. Manage tools -> scopes/limits -> policy gating -> audit changes
- J4. OS Chat: interact with "OS model" to create runs, inspect state, and generate patches

**Success metrics (KPIs)**
- KPI1. Time-to-first-successful-run (median): <= 10 minutes
- KPI2. Failed-run triage time (median): <= 5 minutes to identify primary error class
- KPI3. Run reproducibility rate: >= 95% runs have complete config + trace + artifacts
- KPI4. Cost visibility: >= 90% runs show token/cost breakdown within 10 seconds
- KPI5. Query performance: runs explorer filter response p95 <= 800ms
- KPI6. Operator efficiency: >= 50% key actions via command palette / keyboard
- KPI7. Governance enforcement: 100% policy denials include human-readable reason + rule id

**Scope (MVP -> V1)**
- MVP:
  - Dashboard health/cost
  - Runs Explorer + Run Detail (timeline/logs/artifacts/cost summary)
  - Agents list + agent detail (read-only config snapshot)
  - Secrets status (missing/ok/rotated) + connectors status
  - OS Chat (basic) linked to runs and patch generation
- V1:
  - Agent Builder (prompt/models/tools/memory/policies) + versioning + diff + rollback
  - Replay/fork/compare runs
  - Tools registry + permissions + policy simulation
  - Observability queries (logs/traces/cost analytics)

**Risks / mitigations**
- R1. UI drift from backend behavior -> use typed API contracts + schema validation in UI
- R2. Performance with large tables -> virtualization + server-side filtering + saved queries
- R3. Governance opacity -> standard policy decision envelope + consistent microcopy
- R4. OS Chat confusion -> strict message envelope + tool call visibility + replay links

## Component List + Props (Front-end Contract) (ASCII)

Conventions:
- TypeScript types
- Strict status enums
- All components must support "dense" mode for power users
- Drawer/split-view is a first-class layout primitive

```typescript
export type EnvId = "dev" | "stage" | "prod" | string;

export type RunStatus =
  | "QUEUED"
  | "RUNNING"
  | "WAITING_INPUT"
  | "BLOCKED"
  | "FAILED"
  | "CANCELLED"
  | "SUCCEEDED";

export type ErrorClass =
  | "CONFIG_ERROR"
  | "POLICY_DENIED"
  | "TOOL_ERROR"
  | "MODEL_ERROR"
  | "INFRA_ERROR"
  | "DATA_ERROR";

export type PolicyDecision = "ALLOW" | "DENY" | "REQUIRE_APPROVAL";

export type SortDir = "asc" | "desc";

export interface AppShellProps {
  leftNav: React.ReactNode;
  topBar: React.ReactNode;
  children: React.ReactNode;
  rightDrawer?: React.ReactNode;
  dense?: boolean;
}

export interface RightDrawerProps {
  open: boolean;
  title?: string;
  width?: number;
  onClose: () => void;
  children: React.ReactNode;
}

export interface SplitViewProps {
  left: React.ReactNode;
  right: React.ReactNode;
  rightVisible: boolean;
  onToggleRight: (v: boolean) => void;
  dense?: boolean;
}

export interface ColumnDef<T> {
  id: string;
  header: string;
  width?: number;
  pinned?: "left" | "right";
  accessor: (row: T) => React.ReactNode;
  sortKey?: string;
}

export interface DataTableProps<T> {
  rows: T[];
  columns: ColumnDef<T>[];
  rowKey: (row: T) => string;
  loading?: boolean;
  dense?: boolean;
  selectable?: boolean;
  selectedRowKeys?: string[];
  onSelectionChange?: (keys: string[]) => void;
  onSortChange?: (sortKey: string, dir: SortDir) => void;
  onPageChange?: (page: number) => void;
  page?: number;
  pageSize?: number;
  totalRows?: number;
  visibleColumnIds?: string[];
  onVisibleColumnIdsChange?: (ids: string[]) => void;
  onRowClick?: (row: T) => void;
  rowActions?: (row: T) => React.ReactNode;
}

export type FilterOp =
  | "eq" | "neq"
  | "in" | "not_in"
  | "contains"
  | "gte" | "lte"
  | "between";

export interface FilterClause {
  field: string;
  op: FilterOp;
  value: any;
}

export interface QuerySpec {
  clauses: FilterClause[];
  sort?: { key: string; dir: SortDir };
  timeRange?: { fromIso: string; toIso: string };
}

export interface QueryBuilderProps {
  spec: QuerySpec;
  fields: { name: string; label: string; type: "string" | "number" | "enum" | "time" }[];
  onChange: (spec: QuerySpec) => void;
  onSave?: (name: string, spec: QuerySpec) => void;
  savedQueries?: { id: string; name: string; spec: QuerySpec }[];
  onLoadSaved?: (id: string) => void;
  dense?: boolean;
}

export interface StatusBadgeProps {
  status: RunStatus | string;
  tooltip?: string;
  compact?: boolean;
}

export interface RunSummaryCardProps {
  runId: string;
  status: RunStatus;
  env: EnvId;
  agentName?: string;
  workflowName?: string;
  startedAtIso?: string;
  durationMs?: number;
  tokens?: number;
  costUsd?: number;
  error?: { class: ErrorClass; code?: string; message?: string };
  onCopyRunId?: () => void;
  onOpenRun?: () => void;
}

export interface TimelineStep {
  id: string;
  name: string;
  status: RunStatus | "STEP_RUNNING" | "STEP_DONE" | "STEP_FAILED" | string;
  startedAtIso?: string;
  endedAtIso?: string;
  meta?: Record<string, any>;
}

export interface RunTimelineProps {
  steps: TimelineStep[];
  selectedStepId?: string;
  onSelectStep?: (id: string) => void;
  dense?: boolean;
}

export interface LogViewerProps {
  lines: string[];
  loading?: boolean;
  tailing?: boolean;
  onToggleTailing?: (v: boolean) => void;
  onSearch?: (q: string) => void;
  onCopyAll?: () => void;
  heightPx?: number;
  dense?: boolean;
}

export interface ArtifactItem {
  id: string;
  name: string;
  type: "file" | "json" | "text" | "link";
  sizeBytes?: number;
  createdAtIso?: string;
  downloadUrl?: string;
}

export interface ArtifactsPanelProps {
  artifacts: ArtifactItem[];
  onDownload?: (id: string) => void;
  onOpen?: (id: string) => void;
  dense?: boolean;
}

export interface CostBreakdownRow {
  label: string;
  tokens?: number;
  costUsd?: number;
}

export interface CostBreakdownProps {
  rows: CostBreakdownRow[];
  totalTokens?: number;
  totalCostUsd?: number;
  dense?: boolean;
}

export interface CodeEditorProps {
  value: string;
  language: "json" | "yaml" | "text";
  readOnly?: boolean;
  onChange?: (v: string) => void;
  heightPx?: number;
  validate?: (v: string) => { ok: boolean; errors?: string[] };
  dense?: boolean;
}

export interface DiffViewerProps {
  leftLabel: string;
  rightLabel: string;
  leftValue: string;
  rightValue: string;
  language: "json" | "yaml" | "text";
  dense?: boolean;
}

export interface CommandItem {
  id: string;
  title: string;
  subtitle?: string;
  keywords?: string[];
  run?: () => void;
}

export interface CommandPaletteProps {
  open: boolean;
  items: CommandItem[];
  onClose: () => void;
  onQueryChange?: (q: string) => void;
}

export type ChatRole = "user" | "os" | "agent" | "tool" | "system";

export interface ToolCallEvent {
  id: string;
  toolName: string;
  argsJson: string;
  status: "pending" | "running" | "succeeded" | "failed";
  resultText?: string;
  startedAtIso?: string;
  endedAtIso?: string;
}

export interface ChatMessage {
  id: string;
  role: ChatRole;
  createdAtIso: string;
  contentText: string;
  runId?: string;
  toolCall?: ToolCallEvent;
  meta?: Record<string, any>;
}

export interface ChatThreadProps {
  threadId: string;
  messages: ChatMessage[];
  loading?: boolean;
  onSend: (text: string) => void;
  onStop?: () => void;
  onRetry?: () => void;
  onLinkRun?: (runId: string) => void;
  dense?: boolean;
}

export interface ChatComposerProps {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  disabled?: boolean;
  placeholder?: string;
  showAttachments?: boolean;
}
```

## OpenAPI-like API Contract (JSON) (ASCII)

Notes:
- This is an API "shape" intended for backend + UI alignment.
- All responses use a standard envelope: { ok, data, error, meta }.

```json
{
  "openapi_like": "1.0",
  "basePath": "/api",
  "envelope": {
    "ok": "boolean",
    "data": "any",
    "error": {
      "code": "string",
      "message": "string",
      "details": "any"
    },
    "meta": {
      "requestId": "string",
      "pagination": {
        "page": "number",
        "pageSize": "number",
        "total": "number"
      }
    }
  },
  "schemas": {
    "Agent": {
      "type": "object",
      "required": ["id", "name", "version", "status", "config", "createdAt", "updatedAt"],
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" },
        "description": { "type": "string" },
        "tags": { "type": "array", "items": { "type": "string" } },
        "ownerId": { "type": "string" },
        "version": { "type": "number" },
        "status": { "type": "string" },
        "config": { "type": "object" },
        "createdAt": { "type": "string" },
        "updatedAt": { "type": "string" }
      }
    },
    "Run": {
      "type": "object",
      "required": ["id", "status", "env", "createdAt"],
      "properties": {
        "id": { "type": "string" },
        "agentId": { "type": "string" },
        "workflowId": { "type": "string" },
        "env": { "type": "string" },
        "status": { "type": "string" },
        "trigger": { "type": "object" },
        "inputs": { "type": "object" },
        "outputs": { "type": "object" },
        "metrics": {
          "type": "object",
          "properties": {
            "durationMs": { "type": "number" },
            "tokens": { "type": "number" },
            "costUsd": { "type": "number" }
          }
        },
        "error": {
          "type": "object",
          "properties": {
            "class": { "type": "string" },
            "code": { "type": "string" },
            "message": { "type": "string" }
          }
        },
        "steps": { "type": "array", "items": { "type": "object" } },
        "traceId": { "type": "string" },
        "artifacts": { "type": "array", "items": { "type": "object" } },
        "createdAt": { "type": "string" }
      }
    },
    "Policy": {
      "type": "object",
      "required": ["id", "name", "rules"],
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" },
        "rules": { "type": "array", "items": { "type": "object" } },
        "appliesTo": { "type": "object" }
      }
    },
    "Tool": {
      "type": "object",
      "required": ["id", "name", "capabilities"],
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" },
        "capabilities": { "type": "array", "items": { "type": "string" } },
        "scopes": { "type": "array", "items": { "type": "string" } },
        "limits": { "type": "object" }
      }
    },
    "SecretRef": {
      "type": "object",
      "required": ["id", "name", "status"],
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" },
        "status": { "type": "string" },
        "lastRotatedAt": { "type": "string" }
      }
    },
    "ChatThread": {
      "type": "object",
      "required": ["id", "title", "createdAt"],
      "properties": {
        "id": { "type": "string" },
        "title": { "type": "string" },
        "createdAt": { "type": "string" }
      }
    },
    "ChatMessage": {
      "type": "object",
      "required": ["id", "role", "createdAt", "contentText"],
      "properties": {
        "id": { "type": "string" },
        "role": { "type": "string" },
        "createdAt": { "type": "string" },
        "contentText": { "type": "string" },
        "runId": { "type": "string" },
        "toolCall": { "type": "object" },
        "meta": { "type": "object" }
      }
    }
  },
  "paths": {
    "/healthz": {
      "get": { "resp": "service health summary" }
    },
    "/agents": {
      "get": {
        "query": ["q", "tag", "ownerId", "page", "pageSize", "sortKey", "sortDir"],
        "respSchema": "Agent[]"
      },
      "post": {
        "bodySchema": "Agent",
        "respSchema": "Agent"
      }
    },
    "/agents/{agentId}": {
      "get": { "respSchema": "Agent" },
      "patch": { "bodySchema": "partial Agent", "respSchema": "Agent" }
    },
    "/agents/{agentId}/versions": {
      "get": { "resp": "list versions + metadata" }
    },
    "/runs": {
      "get": {
        "query": ["env", "status", "agentId", "workflowId", "from", "to", "page", "pageSize", "sortKey", "sortDir"],
        "respSchema": "Run[]"
      },
      "post": {
        "body": {
          "agentId": "string",
          "workflowId": "string (optional)",
          "env": "string",
          "inputs": "object",
          "params": "object (optional)"
        },
        "respSchema": "Run"
      }
    },
    "/runs/{runId}": {
      "get": { "respSchema": "Run" }
    },
    "/runs/{runId}/logs": {
      "get": { "query": ["cursor", "limit", "search"], "resp": "log lines + next cursor" }
    },
    "/runs/{runId}/trace": {
      "get": { "resp": "trace spans" }
    },
    "/runs/{runId}/artifacts": {
      "get": { "resp": "ArtifactItem[]" }
    },
    "/runs/{runId}/actions/retry": {
      "post": { "body": { "mode": "same|override", "override": "object (optional)" }, "respSchema": "Run" }
    },
    "/runs/{runId}/actions/fork": {
      "post": { "body": { "newConfig": "object", "inputs": "object" }, "respSchema": "Run" }
    },
    "/tools": {
      "get": { "respSchema": "Tool[]" }
    },
    "/tools/{toolId}": {
      "get": { "respSchema": "Tool" },
      "patch": { "body": { "scopes": "string[]", "limits": "object" }, "respSchema": "Tool" }
    },
    "/policies": {
      "get": { "respSchema": "Policy[]" },
      "post": { "bodySchema": "Policy", "respSchema": "Policy" }
    },
    "/policies/{policyId}": {
      "get": { "respSchema": "Policy" },
      "patch": { "bodySchema": "partial Policy", "respSchema": "Policy" }
    },
    "/secrets": {
      "get": { "respSchema": "SecretRef[]" }
    },
    "/chat/threads": {
      "get": { "respSchema": "ChatThread[]" },
      "post": { "body": { "title": "string" }, "respSchema": "ChatThread" }
    },
    "/chat/threads/{threadId}/messages": {
      "get": { "respSchema": "ChatMessage[]" },
      "post": { "body": { "contentText": "string" }, "respSchema": "ChatMessage" }
    },
    "/chat/threads/{threadId}/actions/stop": {
      "post": { "resp": "stop current streaming response / tool chain" }
    }
  }
}
```

## Microcopy (EN + FA-Latin) (ASCII)

Format: key = EN | FA-Latin

```
app.title = OmertaOS Console | Konsol-e OmertaOS
common.save = Save | Zakhire
common.cancel = Cancel | Laghv
common.close = Close | Baste
common.delete = Delete | Hazf
common.edit = Edit | Virayesh
common.search = Search | Jostejoo
common.filter = Filter | Filtr
common.refresh = Refresh | Baz-sazi
common.copy = Copy | Copy
common.copied = Copied | Copy shod
common.loading = Loading... | Dar hal-e barghozari...
common.error = Something went wrong | Khata rokh dad
common.try_again = Try again | Dobare emtehan kon

dashboard.title = Dashboard | Dashbord
dashboard.health_ok = All services healthy | Hame servis-ha salem
dashboard.health_degraded = Degraded dependencies detected | Vabastegi-ye moshkel darad
dashboard.open_failed_runs = Open failed runs | Baz kardan run-haye failed

runs.title = Runs | Run-ha
runs.empty = No runs found | Hich run-i peyda nashod
runs.bulk_stop = Stop selected | Tavaqof entekhab-shode
runs.bulk_retry = Retry selected | Ejra-ye mojaddad
run.status.QUEUED = Queued | Dar saf
run.status.RUNNING = Running | Dar hal ejra
run.status.WAITING_INPUT = Waiting for input | Montazer-e voroodi
run.status.BLOCKED = Blocked | Masdood
run.status.FAILED = Failed | Namovafaq
run.status.CANCELLED = Cancelled | Laghv shode
run.status.SUCCEEDED = Succeeded | Movafaq

run.detail.title = Run details | Jozeyat-e run
run.detail.replay = Replay | Dobare ejra
run.detail.fork = Fork | Shekafe
run.detail.compare = Compare | Moghayese
run.detail.open_logs = Open logs | Baz kardan log
run.detail.open_trace = Open trace | Baz kardan trace
run.detail.cost = Cost | Hazine
run.detail.artifacts = Artifacts | Khoroji-ha

error.CONFIG_ERROR = Invalid configuration | Kanfig na-dorost
error.POLICY_DENIED = Blocked by policy | Tavasot-e policy masdood shod
error.TOOL_ERROR = Tool failed | Tool kharab shod
error.MODEL_ERROR = Model error | Khata-ye model
error.INFRA_ERROR = Infrastructure issue | Moshkel-e zirsakht
error.DATA_ERROR = Invalid input data | Dade-ye voroodi na-dorost

agents.title = Agents | Agent-ha
agents.new = New agent | Agent-e jadid
agents.publish = Publish | Enteshar
agents.rollback = Roll back | Bazgasht
agents.versions = Versions | Version-ha
agents.builder = Agent builder | Sazande-ye agent

tools.title = Tools | Tool-ha
tools.scopes = Scopes | Scope-ha
secrets.title = Secrets | Secret-ha
secrets.missing = Missing secret | Secret mojood nist
secrets.ok = Secret connected | Secret vasl ast
secrets.rotate = Rotate secret | Charkhesh-e secret

governance.title = Governance | Hakemiyat
policies.title = Policies | Policy-ha
audit.title = Audit log | Log-e audit
policy.simulate = Simulate policy | Shabih-sazi policy

chat.title = OS Chat | Chat-e OS
chat.new_thread = New thread | Thread-e jadid
chat.send = Send | Ersal
chat.stop = Stop | Tavaqof
chat.retry = Retry | Dobare
chat.placeholder = Ask the OS to run, debug, or patch | Az OS bekhah: run, debug, patch
chat.tool_call = Tool call | Tool call
chat.link_run = Link run | Vasl kardan run
chat.open_run = Open run | Baz kardan run
```

## OS Chat Section for Codex (ASCII)

### OS Chat UI wireframe (ASCII)

```
+-----------------------------------------+
| TopBar: [Workspace] [Env: prod] [Search] [Cmd+K]                     [Alerts]   |
+-----------+--------------------+
| Left Nav             | OS Chat (thread: )                                  |
| - Dashboard          |--------------------|
| - Runs               | Messages                                                   |
| - Agents             |  [user]  "Create an agent for X and run it on Y"           |
| - Workflows          |  [os]    "Plan: 1) validate secrets 2) create draft ..."   |
| - Tools              |  [tool]  toolName=repo_scan status=running                 |
| - Memory             |  [tool]  result: "Found config files: ..."                 |
| - Observability      |  [os]    "Created run run_123. Open run?" [Open] [Link]    |
| - Governance         |--------------------|
| - Settings           | Composer: [___________________________] [Send] [Stop]      |
+-----------+--------------------+
```

### OS Chat message envelope (strict, deterministic)

OS message example:

```
{
  "threadId": "thr_1",
  "message": {
    "id": "msg_1",
    "role": "os",
    "createdAtIso": "2025-12-14T12:00:00Z",
    "contentText": "I can create the agent, validate secrets, and run a smoke test.",
    "meta": {
      "intent": "create_agent_and_run",
      "env": "prod",
      "requestedActions": ["validate_secrets", "create_agent", "run_smoke_test"]
    }
  }
}
```

Tool-call event message:

```
{
  "id": "msg_2",
  "role": "tool",
  "createdAtIso": "2025-12-14T12:00:02Z",
  "contentText": "tool_call repo_scan",
  "toolCall": {
    "id": "tc_1",
    "toolName": "repo_scan",
    "argsJson": "{\"paths\":[\"./\"],\"include\":\"docs\"}",
    "status": "running",
    "resultText": ""
  }
}
```

Run-linking OS message:

```
{
  "id": "msg_5",
  "role": "os",
  "createdAtIso": "2025-12-14T12:01:10Z",
  "contentText": "Run created: run_123 (FAILED: TOOL_ERROR HTTP_504). Suggested fix: increase timeout.",
  "runId": "run_123",
  "meta": {
    "errorClass": "TOOL_ERROR",
    "errorCode": "HTTP_504",
    "suggestedActions": ["retry_with_override", "disable_tool_temporarily"]
  }
}
```

### OS Chat backend endpoints (minimal for MVP)
- POST /api/chat/threads
- GET /api/chat/threads
- GET /api/chat/threads/{threadId}/messages
- POST /api/chat/threads/{threadId}/messages (user sends text)
- POST /api/chat/threads/{threadId}/actions/stop
- (optional) SSE/WS: /api/chat/threads/{threadId}/stream for live tokens/tool status

### OS Chat "Codex prompt" (ASCII)

Use this as a single prompt to Codex:

```
You are a senior full-stack engineer. Implement an "OS Chat" page in the console app with
a deterministic message model and visible tool-call events.

Requirements:
1) Routes:
   - /chat : list threads, create new thread
   - /chat/[threadId] : chat thread view (messages + composer)
2) Data model (front-end types):
   - ChatMessage { id, role: user|os|agent|tool|system, createdAtIso, contentText, runId?, toolCall? }
   - ToolCallEvent { id, toolName, argsJson, status: pending|running|succeeded|failed, resultText? }
3) UI:
   - Split view: thread list left, active chat right (or thread list modal in small screens)
   - Messages show role badge, timestamp, and allow copy
   - Tool-call messages render as collapsible blocks showing argsJson and resultText
   - If message has runId, show "Open run" button linking to /runs/[runId]
   - Composer supports Enter to send, Shift+Enter newline, and Stop button during streaming
4) State:
   - Optimistic send for user messages
   - Streaming mode: OS responses arrive incrementally (SSE or polling)
   - Tool-call status updates in-place
5) API integration:
   - GET /api/chat/threads
   - POST /api/chat/threads { title }
   - GET /api/chat/threads/{threadId}/messages
   - POST /api/chat/threads/{threadId}/messages { contentText }
   - POST /api/chat/threads/{threadId}/actions/stop
6) Error handling:
   - Standard envelope { ok, data, error, meta }
   - Show inline retry on failures
7) Accessibility:
   - Keyboard navigation for message list and command palette integration
8) Code quality:
   - Add typed API client functions
   - Add unit tests for message rendering and tool-call collapse behavior
   - Keep styling consistent with dense admin console design

Deliverables:
- New pages/components
- TypeScript types
- API client module
- Minimal CSS/Tailwind (whichever project uses)
- Tests
```

### OS Chat "OS model" behavior contract

- The OS responds with plain text plus structured meta.
- Any external action must appear as a tool-call message.
- Any run creation must return a runId and link to Runs UI.
- Policy denials must return a rule id and human text in contentText.
- Reproducibility: OS must attach config snapshots in artifacts or meta references.

Minimal OS intents (meta.intent):
- create_agent
- update_agent
- run_agent
- inspect_run
- propose_patch
- apply_patch (if permitted)
- explain_policy
- rotate_secret (if permitted)

If desired, a fake backend fixture can be added so the UI can be developed and tested before the real OS runtime is wired.
