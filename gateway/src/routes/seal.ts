import createError from 'http-errors';
import type { FastifyInstance, FastifyRequest } from 'fastify';

import { gatewayConfig } from '../config.js';

const headers = () => {
  const data: Record<string, string> = { 'content-type': 'application/json' };
  if (gatewayConfig.adminToken) {
    data.authorization = `Bearer ${gatewayConfig.adminToken}`;
  }
  return data;
};

const requireAdmin = (request: FastifyRequest) => {
  const roles = request.aionContext.user?.roles ?? [];
  if (!roles.includes('admin')) {
    throw createError(403, 'Admin privileges required');
  }
};

const proxySeal = async <T>(method: 'GET' | 'POST', path: string, body?: unknown): Promise<T> => {
  const response = await fetch(`${gatewayConfig.controlBaseUrl}${path}`, {
    method,
    headers: headers(),
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    const text = await response.text();
    throw createError(response.status, text || 'seal proxy failed');
  }
  if (response.status === 204) {
    return {} as T;
  }
  return (await response.json()) as T;
};

export const registerSealRoutes = (app: FastifyInstance) => {
  if (!gatewayConfig.featureSeal) {
    return;
  }

  app.post('/v1/seal/jobs', async (request, _reply) => {
    requireAdmin(request);
    const payload = (request.body ?? {}) as Record<string, unknown>;
    return proxySeal('POST', '/v1/seal/jobs', payload);
  });

  app.get('/v1/seal/jobs/:id/status', async (request, _reply) => {
    requireAdmin(request);
    const { id } = request.params as { id: string };
    return proxySeal('GET', `/v1/seal/jobs/${id}/status`);
  });

  app.get('/v1/seal/streams/:id', async (request, _reply) => {
    requireAdmin(request);
    const { id } = request.params as { id: string };
    return proxySeal('GET', `/v1/seal/streams/${id}`);
  });

  app.post('/v1/router/policy/reload', async (request, _reply) => {
    requireAdmin(request);
    return proxySeal('POST', '/v1/seal/router/policy/reload');
  });
};
