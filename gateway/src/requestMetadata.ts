import type { FastifyRequest } from 'fastify';
import { Metadata } from '@grpc/grpc-js';

import { tenantFromHeader } from './auth/claims.js';

const addHeader = (metadata: Metadata, request: FastifyRequest, name: string) => {
  const value = request.headers[name];
  if (typeof value === 'string' && value.trim()) {
    metadata.add(name, value.trim());
  }
};

export const buildControlMetadata = (request: FastifyRequest): Metadata => {
  const metadata = new Metadata();
  metadata.add('x-request-id', request.id);
  addHeader(metadata, request, 'x-correlation-id');
  addHeader(metadata, request, 'traceparent');
  addHeader(metadata, request, 'idempotency-key');
  addHeader(metadata, request, 'authorization');

  const tenant = tenantFromHeader(request);
  if (tenant) {
    metadata.add('tenant-id', tenant);
  }
  return metadata;
};
