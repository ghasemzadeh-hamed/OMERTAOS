export interface TaskPayload {
  intent: string
  params: Record<string, unknown>
  preferred_engine?: 'local' | 'api' | 'hybrid'
  priority?: number
  meta?: Record<string, unknown>
}

export interface Task extends TaskPayload {
  id: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  result?: Record<string, unknown>
}
