import type { FastifyRequest } from 'fastify';
import { describe, expect, it } from 'vitest';

import { buildNetworkControlHeaders } from '../../gateway/src/routes/network.js';

describe('Network Control service authentication', () => {
  it('authenticates Gateway reads before forwarding user roles', () => {
    const request = {
      id: 'request-network-1',
      aionContext: {
        requestId: 'request-network-1',
        authType: 'api_key',
        user: {
          id: 'user-1',
          roles: ['user'],
          tenant: 'tenant-a',
        },
      },
    } as unknown as FastifyRequest;

    const headers = buildNetworkControlHeaders(request);

    expect(headers.authorization).toBe('Bearer test-admin-token');
    expect(headers['x-aion-roles']).toBe('user');
    expect(headers['x-aion-user-id']).toBe('user-1');
    expect(headers['tenant-id']).toBe('tenant-a');
  });
});
