import { beforeEach, describe, expect, it, vi } from 'vitest';

describe('OS chat store', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('starts without seeded demo threads or messages', async () => {
    const store = await import('@/lib/osChatStore');

    expect(store.listThreads().data).toEqual([]);
  });

  it('stores only source-backed messages added by the chat route', async () => {
    const store = await import('@/lib/osChatStore');
    const thread = store.createThread('Live task').data;

    store.addMessage(thread.id, 'Run the health check');
    store.addAssistantMessage(thread.id, 'Task completed', {
      runId: 'task-1',
      meta: { status: 'OK' },
    });

    expect(store.getMessages(thread.id).data).toEqual([
      expect.objectContaining({ role: 'user', contentText: 'Run the health check' }),
      expect.objectContaining({ role: 'os', contentText: 'Task completed', runId: 'task-1' }),
    ]);
  });
});
