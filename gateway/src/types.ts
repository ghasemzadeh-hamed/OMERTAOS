import { z } from 'zod';

export const taskRequestSchema = z
  .object({
    schemaVersion: z.string().min(1).default('1.0'),
    intent: z.string().min(1, 'intent is required'),
    params: z.record(z.unknown()).default({}),
    preferredEngine: z.enum(['auto', 'local', 'api', 'hybrid']).default('auto'),
    priority: z.enum(['low', 'normal', 'high']).default('normal'),
    sla: z
      .object({
        budget_usd: z.number().positive().finite().optional(),
        p95_ms: z.number().int().positive().optional(),
        privacy: z.enum(['local-only', 'allow-api', 'hybrid']).optional(),
      })
      .partial()
      .optional(),
    metadata: z.record(z.unknown()).optional(),
  })
  .strict();

export type TaskRequestInput = z.input<typeof taskRequestSchema>;
export type TaskRequest = z.output<typeof taskRequestSchema>;

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
