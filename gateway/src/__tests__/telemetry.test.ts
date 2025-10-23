import { describe, it, expect, vi } from 'vitest';
import { TelemetryBroker } from '../telemetry.js';

describe('TelemetryBroker', () => {
  it('notifies subscribers of events', () => {
    const broker = new TelemetryBroker();
    const listener = vi.fn();
    const unsubscribe = broker.subscribe('task-1', listener);
    broker.publish({ taskId: 'task-1', status: 'running', timestamp: new Date().toISOString() });
    expect(listener).toHaveBeenCalledOnce();
    unsubscribe();
    broker.publish({ taskId: 'task-1', status: 'completed', timestamp: new Date().toISOString() });
    expect(listener).toHaveBeenCalledTimes(1);
  });
});
