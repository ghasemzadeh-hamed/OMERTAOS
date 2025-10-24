import type { FastifyRequest } from 'fastify';

export interface ClaimContext {
  tenantId?: string;
}

export const resolveTenant = (request: FastifyRequest, tokenTenant?: string): ClaimContext => {
  const headerTenant = request.headers['x-tenant'];
  if (typeof headerTenant === 'string' && headerTenant.trim()) {
    return { tenantId: headerTenant.trim() };
  }
  if (tokenTenant) {
    return { tenantId: tokenTenant };
  }
  return {};
};
