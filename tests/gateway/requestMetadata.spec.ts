import type { FastifyRequest } from 'fastify';
import { describe, expect, it } from 'vitest';

import { buildControlMetadata } from '../../gateway/src/requestMetadata.js';

describe('Control gRPC request metadata', () => {
  it('propagates bounded request context and normalizes the tenant alias', () => {
    const request = {
      id: 'gateway-request-a',
      headers: {
        authorization: 'Bearer gateway-token',
        'x-tenant-id': ' tenant-a ',
        'x-correlation-id': ' correlation-a ',
        traceparent: ' 00-trace-a-span-a-01 ',
        'idempotency-key': ' idem-a ',
      },
    } as unknown as FastifyRequest;

    const metadata = buildControlMetadata(request);

    expect(metadata.get('x-request-id')).toEqual(['gateway-request-a']);
    expect(metadata.get('x-correlation-id')).toEqual(['correlation-a']);
    expect(metadata.get('traceparent')).toEqual(['00-trace-a-span-a-01']);
    expect(metadata.get('idempotency-key')).toEqual(['idem-a']);
    expect(metadata.get('tenant-id')).toEqual(['tenant-a']);
    expect(metadata.get('authorization')).toEqual(['Bearer gateway-token']);
  });
});
