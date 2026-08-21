import createError from 'http-errors';
import type { FastifyInstance, FastifyRequest } from 'fastify';

import { gatewayConfig } from '../config.js';
import { devBypassAuth, isPublicSetupRoute } from '../auth/index.js';

type KernelProfile = 'user' | 'professional' | 'enterprise-vip';

interface ProfileState {
  profile: KernelProfile;
  setupDone: boolean;
}

let devProfileState: ProfileState = { profile: 'user', setupDone: false };

const controlHeaders = () => {
  const headers: Record<string, string> = { 'content-type': 'application/json' };
  if (gatewayConfig.adminToken) {
    headers.authorization = `Bearer ${gatewayConfig.adminToken}`;
  }
  return headers;
};

const requireAdmin = (request: FastifyRequest) => {
  if (devBypassAuth && isPublicSetupRoute(request)) {
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
    return proxyControl('POST', '/config/propose', payload);
  });

  app.post('/v1/config/apply', async (request, _reply) => {
    requireAdmin(request);
    return proxyControl('POST', '/config/apply');
  });

  app.post('/v1/config/revert', async (request, _reply) => {
    requireAdmin(request);
    return proxyControl('POST', '/config/revert');
  });

  app.get('/v1/config/status', async (request, _reply) => {
    requireAdmin(request);
    return proxyControl('GET', '/config/status');
  });

  // Profile selection is stored canonically inside control (backed by .aion/profile.json).
  // Public in dev/quickstart for setup bootstrap. Protected by JWT in production.
  app.get('/v1/config/profile', async (request) => {
    if (devBypassAuth) {
      // In dev/quickstart the profile lives only in memory to bootstrap the setup wizard.
      return devProfileState;
    }

    try {
      return await proxyControl('GET', '/config/profile');
    } catch (error) {
      request.log.error({ err: error, msg: 'Failed to fetch profile from control' });
      throw error;
    }
  });

  // Public in dev/quickstart for setup bootstrap. Protected by JWT in production.
  app.post('/v1/config/profile', async (request, _reply) => {
    if (devBypassAuth) {
      const payload = (request.body ?? {}) as Partial<ProfileState>;
      if (payload.profile && !['user', 'professional', 'enterprise-vip'].includes(payload.profile)) {
        throw createError(400, 'Invalid profile');
      }

      devProfileState = {
        profile: (payload.profile as KernelProfile) ?? devProfileState.profile,
        setupDone: typeof payload.setupDone === 'boolean' ? payload.setupDone : devProfileState.setupDone,
      };

      return devProfileState;
    }

    requireAdmin(request);
    const payload = (request.body ?? {}) as Record<string, unknown>;
    try {
      return await proxyControl('POST', '/config/profile', payload);
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
