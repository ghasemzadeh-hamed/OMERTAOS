import createError from 'http-errors';
import type { FastifyInstance, FastifyRequest } from 'fastify';

import { gatewayConfig } from '../config.js';

const controlHeaders = () => {
  const headers: Record<string, string> = { 'content-type': 'application/json' };
  if (gatewayConfig.adminToken) {
    headers.authorization = `Bearer ${gatewayConfig.adminToken}`;
  }
  return headers;
};

const requireAdmin = (request: FastifyRequest) => {
  const roles = request.aionContext.user?.roles ?? [];
  if (!roles.includes('admin')) {
    throw createError(403, 'Admin privileges required');
  }
};

const proxyControl = async <T>(
  method: 'GET' | 'POST',
  path: string,
  body?: unknown,
): Promise<T> => {
  const response = await fetch(`${gatewayConfig.controlBaseUrl}${path}`, {
    method,
    headers: controlHeaders(),
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    const text = await response.text();
    throw createError(response.status, text || 'control request failed');
  }
  if (response.status === 204) {
    return {} as T;
  }
  return (await response.json()) as T;
};

export const registerConfigRoutes = (app: FastifyInstance) => {
  app.post('/v1/config/propose', async (request, _reply) => {
    requireAdmin(request);
    const payload = (request.body ?? {}) as Record<string, unknown>;
    return proxyControl('POST', '/v1/config/propose', payload);
  });

  app.post('/v1/config/apply', async (request, _reply) => {
    requireAdmin(request);
    return proxyControl('POST', '/v1/config/apply');
  });

  app.post('/v1/config/revert', async (request, _reply) => {
    requireAdmin(request);
    return proxyControl('POST', '/v1/config/revert');
  });

  app.get('/v1/config/status', async (request, _reply) => {
    requireAdmin(request);
    return proxyControl('GET', '/v1/config/status');
  });

  app.get('/v1/models', async () => {
    try {
      return await proxyControl('GET', '/models');
    } catch (error) {
      return [
        {
          name: gatewayConfig.profile === 'enterprise-vip' ? 'seal-advisor' : 'local-router',
          provider: 'local',
          profile: gatewayConfig.profile,
        },
      ];
    }
  });
};
