import { FastifyReply, FastifyRequest } from 'fastify';
import createError from 'http-errors';
import jwt from 'jsonwebtoken';
import { gatewayConfig } from '../config.js';
import { resolveTenant } from './claims.js';

export interface RequestContext {
  requestId: string;
  user: {
    id: string;
    roles: string[];
    tenant?: string;
    metadata?: Record<string, unknown>;
  } | null;
  authType: 'api_key' | 'jwt' | 'anonymous';
}

declare module 'fastify' {
  interface FastifyRequest {
    aionContext: RequestContext;
  }
}

export const buildDefaultContext = (request: FastifyRequest): RequestContext => ({
  requestId: request.id,
  user: null,
  authType: 'anonymous',
});

const ensureRole = (roles: string[], required: string[]): boolean => {
  return required.some((role) => roles.includes(role));
};

const isDevMode =
  process.env.AION_ENV === 'dev' ||
  process.env.AION_AUTH_MODE === 'disabled' ||
  process.env.NODE_ENV === 'development';

const isDevAuthMode = gatewayConfig.environment === 'development' || isDevMode;

const PUBLIC_SETUP_ROUTES = ['/v1/config/profile'];

const isPublicSetupRoute = (request: FastifyRequest): boolean => {
  const path = request.routerPath ?? request.routeOptions?.url ?? request.url;
  return PUBLIC_SETUP_ROUTES.includes(path);
};

let jwtMissingWarningLogged = false;

const warnMissingJwtOnce = (request?: FastifyRequest) => {
  if (jwtMissingWarningLogged || !isDevMode || gatewayConfig.jwtPublicKey) {
    return;
  }
  const message =
    'Gateway JWT public key not configured; in dev mode setup routes will bypass authentication.';
  if (request) {
    request.log.warn(message);
  } else {
    // eslint-disable-next-line no-console
    console.warn(message);
  }
  jwtMissingWarningLogged = true;
};

const decodeJwt = (token: string, request: FastifyRequest) => {
  const publicKey = gatewayConfig.jwtPublicKey;
  if (!publicKey) {
    warnMissingJwtOnce(request);
    throw createError(401, 'Authentication required');
  }
  return jwt.verify(token, publicKey, { algorithms: ['RS256'] });
};

export const authPreHandler = (requiredRoles: string[] = []) => {
  return async (request: FastifyRequest, _reply: FastifyReply) => {
    const context = buildDefaultContext(request);
    const publicRoutes = new Set(['/healthz', '/health', '/readyz']);
    if (publicRoutes.has(request.routerPath ?? '')) {
      request.aionContext = context;
      return;
    }

    if (isDevMode && isPublicSetupRoute(request)) {
      warnMissingJwtOnce(request);
      request.aionContext = context;
      return;
    }

    if (gatewayConfig.environment === 'test') {
      request.aionContext = {
        ...context,
        authType: 'api_key',
        user: {
          id: 'test-runner',
          roles: requiredRoles.length ? requiredRoles : ['user'],
          tenant: resolveTenant(request, undefined).tenantId,
        },
      };
      return;
    }

    const apiKey = request.headers['x-api-key'];
    if (typeof apiKey === 'string' && gatewayConfig.apiKeys[apiKey]) {
      const keyConfig = gatewayConfig.apiKeys[apiKey];
      const tenant = resolveTenant(request, keyConfig.tenant).tenantId;
      context.user = {
        id: `api-key:${apiKey.slice(0, 6)}`,
        roles: keyConfig.roles,
        tenant,
      };
      context.authType = 'api_key';
    } else if (typeof request.headers.authorization === 'string') {
      const token = request.headers.authorization.replace('Bearer ', '');
      const payload = decodeJwt(token, request) as jwt.JwtPayload;
      const roles = Array.isArray(payload.roles)
        ? (payload.roles as string[])
        : typeof payload.role === 'string'
        ? payload.role.split(',')
        : [];
      const tenant = resolveTenant(request, payload.tenant_id ? String(payload.tenant_id) : undefined).tenantId;
      context.user = {
        id: String(payload.sub || payload.user_id || 'unknown'),
        roles,
        tenant,
        metadata: payload,
      };
      context.authType = 'jwt';
    }

    if (!context.user && requiredRoles.length > 0) {
      throw createError(401, 'Authentication required');
    }

    if (context.user && requiredRoles.length > 0 && !ensureRole(context.user.roles, requiredRoles)) {
      throw createError(403, 'Forbidden');
    }

    request.aionContext = context;
  };
};

if (isDevMode && !gatewayConfig.jwtPublicKey) {
  warnMissingJwtOnce();
}

export { isDevAuthMode, isPublicSetupRoute, PUBLIC_SETUP_ROUTES, isDevMode };
