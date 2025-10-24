export type TaskStatus = 'PENDING' | 'RUNNING' | 'OK' | 'ERROR' | 'TIMEOUT' | 'CANCELED';

export interface Task {
  taskId: string;
  intent: string;
  params: Record<string, unknown>;
  status: TaskStatus;
  result?: Record<string, unknown>;
  createdAt?: string;
  updatedAt?: string;
  tenantId?: string;
}
