import type { FastifyRequest } from 'fastify';

export interface ClaimContext {
  tenantId?: string;
}

const TENANT_HEADERS = ['tenant-id', 'x-tenant-id', 'x-tenant'];

export const tenantFromHeader = (request: FastifyRequest): string | undefined => {
  for (const header of TENANT_HEADERS) {
    const value = request.headers[header];
    if (typeof value === 'string' && value.trim()) {
      return value.trim();
    }
  }
  return undefined;
};

export const resolveTenant = (request: FastifyRequest, tokenTenant?: string): ClaimContext => {
  const headerTenant = tenantFromHeader(request);
  if (headerTenant) {
    return { tenantId: headerTenant };
  }
  if (tokenTenant) {
    return { tenantId: tokenTenant };
  }
  return {};
};

export const tenantHeaderNames = TENANT_HEADERS;
