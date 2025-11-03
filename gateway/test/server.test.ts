import { describe, expect, it } from 'vitest';
import app from '../src/server.js';

describe('gateway server configuration', () => {
  it('exposes health endpoints', async () => {
    for (const endpoint of ['/healthz', '/health']) {
      const response = await app.inject({ method: 'GET', url: endpoint });
      expect(response.statusCode).toBe(200);
      const payload = response.json();
      expect(['ok', 'degraded']).toContain(payload.status);
      expect(payload.service).toBe('gateway');
    }
  });

  it('rejects invalid task payloads early', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/v1/tasks',
      payload: { intent: '' },
    });

    expect(response.statusCode).toBe(400);
    const payload = response.json();
    expect(payload.error).toBe('ValidationError');
    expect(payload.issues).toBeInstanceOf(Array);
    expect(payload.issues[0]?.path).toContain('intent');
  });
});
