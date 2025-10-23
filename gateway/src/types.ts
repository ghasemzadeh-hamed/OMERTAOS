export interface TaskRequest {
  task_id: string;
  intent: string;
  params: Record<string, unknown>;
  preferred_engine?: 'local' | 'api' | 'hybrid';
  priority?: 'low' | 'medium' | 'high';
  meta?: Record<string, unknown>;
}

export interface TaskResponse {
  decision: 'local' | 'api' | 'hybrid';
  reason: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  result?: Record<string, unknown> | null;
  error?: string | null;
}

export interface TelemetryEvent {
  taskId: string;
  status: TaskResponse['status'];
  timestamp: string;
  message?: string;
}
