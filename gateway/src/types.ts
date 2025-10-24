export interface TaskRequest {
  schemaVersion: string;
  intent: string;
  params: Record<string, unknown>;
  preferredEngine?: 'auto' | 'local' | 'api' | 'hybrid';
  priority?: 'low' | 'normal' | 'high';
  sla?: {
    budget_usd?: number;
    p95_ms?: number;
    privacy?: 'local-only' | 'allow-api' | 'hybrid';
  };
  metadata?: Record<string, unknown>;
}

export interface TaskResult {
  schemaVersion: string;
  taskId: string;
  intent: string;
  status: 'PENDING' | 'RUNNING' | 'OK' | 'ERROR' | 'TIMEOUT' | 'CANCELED';
  engine: {
    route: string;
    chosen_by: string;
    reason: string;
    tier?: string;
  };
  result?: Record<string, unknown>;
  usage?: {
    latency_ms?: number;
    tokens?: number;
    cost_usd?: number;
  };
  error?: {
    code: string;
    message: string;
  } | null;
}
