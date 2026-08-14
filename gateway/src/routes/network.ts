import createError from 'http-errors';
import type { FastifyInstance, FastifyRequest } from 'fastify';

import { devBypassAuth } from '../auth/index.js';
import { gatewayConfig } from '../config.js';

type ControlMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

const requireAdmin = (request: FastifyRequest) => {
  if (devBypassAuth) {
    return;
  }
  const roles = request.aionContext.user?.roles ?? [];
  if (!roles.includes('admin')) {
    throw createError(403, 'Admin privileges required');
  }
};

const controlHeaders = (request: FastifyRequest, includeServiceToken: boolean) => {
  const headers: Record<string, string> = { 'content-type': 'application/json' };
  if (includeServiceToken && gatewayConfig.adminToken) {
    headers.authorization = `Bearer ${gatewayConfig.adminToken}`;
  }
  const roles = request.aionContext.user?.roles ?? [];
  if (roles.length > 0) {
    headers['x-aion-roles'] = roles.join(',');
  }
  if (request.aionContext.user?.id) {
    headers['x-aion-user-id'] = request.aionContext.user.id;
  }
  if (request.aionContext.user?.tenant) {
    headers['tenant-id'] = request.aionContext.user.tenant;
  }
  headers['x-request-id'] = request.id;
  return headers;
};

const proxyControl = async <T>(
  request: FastifyRequest,
  method: ControlMethod,
  path: string,
  body?: unknown,
  includeServiceToken = true,
): Promise<T> => {
  const response = await fetch(`${gatewayConfig.controlBaseUrl}${path}`, {
    method,
    headers: controlHeaders(request, includeServiceToken),
    body: body === undefined ? undefined : JSON.stringify(body),
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

export const registerNetworkRoutes = (app: FastifyInstance) => {
  app.get('/v1/network/proxies', async (request) => {
    return proxyControl(request, 'GET', '/network/proxies', undefined, false);
  });

  app.post('/v1/network/proxies', async (request) => {
    requireAdmin(request);
    return proxyControl(request, 'POST', '/network/proxies', request.body ?? {});
  });

  app.get('/v1/network/proxies/:id', async (request) => {
    const { id } = request.params as { id: string };
    return proxyControl(request, 'GET', `/network/proxies/${encodeURIComponent(id)}`, undefined, false);
  });

  app.put('/v1/network/proxies/:id', async (request) => {
    requireAdmin(request);
    const { id } = request.params as { id: string };
    return proxyControl(request, 'PUT', `/network/proxies/${encodeURIComponent(id)}`, request.body ?? {});
  });

  app.delete('/v1/network/proxies/:id', async (request, reply) => {
    requireAdmin(request);
    const { id } = request.params as { id: string };
    await proxyControl(request, 'DELETE', `/network/proxies/${encodeURIComponent(id)}`);
    return reply.status(204).send();
  });

  for (const action of ['enable', 'disable', 'test', 'set-default'] as const) {
    app.post(`/v1/network/proxies/:id/${action}`, async (request) => {
      requireAdmin(request);
      const { id } = request.params as { id: string };
      return proxyControl(
        request,
        'POST',
        `/network/proxies/${encodeURIComponent(id)}/${action}`,
        request.body ?? {},
      );
    });
  }
};
