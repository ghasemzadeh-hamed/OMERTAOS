import { describe, expect, it } from 'vitest';
import app from '../src/server.js';

describe('gateway server configuration', () => {
  it('exposes health endpoint', async () => {
    const response = await app.inject({ method: 'GET', url: '/healthz' });
    expect(response.statusCode).toBe(200);
    const payload = response.json();
    expect(['ok', 'degraded']).toContain(payload.status);
  });
});
