import { describe, expect, it } from 'vitest';
import { taskRequestSchema } from '../src/types.js';

describe('taskRequestSchema', () => {
  it('applies defaults for optional fields', () => {
    const parsed = taskRequestSchema.parse({ intent: 'summarize' });
    expect(parsed.schemaVersion).toBe('1.0');
    expect(parsed.params).toEqual({});
    expect(parsed.preferredEngine).toBe('auto');
    expect(parsed.priority).toBe('normal');
  });

  it('rejects invalid SLA constraints', () => {
    expect(() =>
      taskRequestSchema.parse({
        intent: 'classify',
        sla: { budget_usd: -1 },
      })
    ).toThrowError(/Number must be greater than 0/);
  });
});
