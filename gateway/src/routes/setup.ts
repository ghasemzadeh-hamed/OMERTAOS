import type { FastifyInstance } from 'fastify';

import { gatewayConfig } from '../config.js';

const kernelProfiles = [
  { id: 'user', label: 'User', description: 'Default single-tenant developer profile.' },
  {
    id: 'professional',
    label: 'Professional',
    description: 'Multi-user profile with team-ready defaults.',
  },
  {
    id: 'enterprise-vip',
    label: 'Enterprise',
    description: 'Enterprise profile with seal advisor enabled.',
  },
];

export const registerSetupRoutes = (app: FastifyInstance) => {
  const proxyControl = async <T>(method: 'GET' | 'POST', path: string, body?: unknown): Promise<T> => {
    const response = await fetch(`${gatewayConfig.controlBaseUrl}${path}`, {
      method,
      headers: { 'content-type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || 'control request failed');
    }
    return (await response.json()) as T;
  };

  app.get('/v1/setup/profile', async () => {
    return {
      profiles: kernelProfiles,
      setupDone: false,
      defaultProfile: 'user',
      updatedAt: new Date().toISOString(),
    };
  });

  app.get('/v1/setup/bootstrap', async () => proxyControl('GET', '/v1/setup/bootstrap'));

  app.post('/v1/setup/bootstrap', async (request) => {
    const payload = (request.body ?? {}) as Record<string, unknown>;
    return proxyControl('POST', '/v1/setup/bootstrap', payload);
  });
};
