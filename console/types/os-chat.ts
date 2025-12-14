export type ChatRole = 'user' | 'os' | 'agent' | 'tool' | 'system';

export type ToolCallStatus = 'pending' | 'running' | 'succeeded' | 'failed';

export interface ToolCallEvent {
  id: string;
  toolName: string;
  argsJson: string;
  status: ToolCallStatus;
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

export interface ChatThread {
  id: string;
  title: string;
  createdAtIso: string;
}

export interface ApiEnvelope<T> {
  ok: boolean;
  data: T;
  error?: { code: string; message: string; details?: any };
  meta?: {
    requestId?: string;
    pagination?: { page: number; pageSize: number; total: number };
  };
}
