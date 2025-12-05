import createError from 'http-errors';
import type { FastifyInstance, FastifyRequest } from 'fastify';

import { gatewayConfig } from '../config.js';
import { isDevAuthMode, isPublicSetupRoute } from '../auth/index.js';

const controlHeaders = () => {
  const headers: Record<string, string> = { 'content-type': 'application/json' };
  if (gatewayConfig.adminToken) {
    headers.authorization = `Bearer ${gatewayConfig.adminToken}`;
  }
  return headers;
};

const requireAdmin = (request: FastifyRequest) => {
  if (isDevAuthMode && isPublicSetupRoute(request)) {
    // During initial bootstrap in dev/quickstart we allow unauthenticated
    // access so the console setup wizard can persist the chosen profile.
    return;
  }

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

  // Profile selection is stored canonically inside control (backed by .aionos/profile.json).
  // Auth is handled by the global middleware; in dev/quickstart we intentionally allow
  // unauthenticated bootstrap so the setup wizard can run before login exists.
  app.get('/v1/config/profile', async (request) => {
    try {
      return await proxyControl('GET', '/v1/config/profile');
    } catch (error) {
      request.log.error({ err: error, msg: 'Failed to fetch profile from control' });
      throw error;
    }
  });

  app.post('/v1/config/profile', async (request, _reply) => {
    requireAdmin(request);
    const payload = (request.body ?? {}) as Record<string, unknown>;
    try {
      return await proxyControl('POST', '/v1/config/profile', payload);
    } catch (error) {
      request.log.error({ err: error, msg: 'Failed to persist profile to control', payload });
      throw error;
    }
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
