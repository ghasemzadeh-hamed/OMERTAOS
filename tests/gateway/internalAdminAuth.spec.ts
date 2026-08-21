import type { FastifyReply, FastifyRequest } from 'fastify';
import { beforeEach, describe, expect, it, vi } from 'vitest';

describe('internal console admin authentication', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('accepts the configured internal admin token without exposing it as a browser API key', async () => {
    const { authPreHandler } = await import('../../gateway/src/auth/index.js');
    const request = {
      id: 'request-1',
      headers: { 'x-aion-admin-token': 'test-admin-token' },
      routeOptions: { url: '/v1/tasks' },
      url: '/v1/tasks',
    } as unknown as FastifyRequest;

    await authPreHandler(['admin'])(request, {} as FastifyReply);

    expect(request.aionContext.user).toMatchObject({
      id: 'internal:console',
      roles: ['user', 'manager', 'admin'],
    });
  });

  it('rejects an invalid internal admin token', async () => {
    const { authPreHandler } = await import('../../gateway/src/auth/index.js');
    const request = {
      id: 'request-2',
      headers: { 'x-aion-admin-token': 'wrong-token' },
      routeOptions: { url: '/v1/tasks' },
      url: '/v1/tasks',
    } as unknown as FastifyRequest;

    await expect(authPreHandler(['admin'])(request, {} as FastifyReply)).rejects.toMatchObject({ statusCode: 503 });
  });
});
