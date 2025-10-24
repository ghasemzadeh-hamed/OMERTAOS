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
    context: RequestContext;
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

const decodeJwt = (token: string) => {
  const publicKey = gatewayConfig.jwtPublicKey;
  if (!publicKey) {
    throw createError(401, 'JWT authentication not configured');
  }
  return jwt.verify(token, publicKey, { algorithms: ['RS256'] });
};

export const authPreHandler = (requiredRoles: string[] = []) => {
  return async (request: FastifyRequest, _reply: FastifyReply) => {
    const context = buildDefaultContext(request);
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
      const payload = decodeJwt(token) as jwt.JwtPayload;
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

    request.context = context;
  };
};
