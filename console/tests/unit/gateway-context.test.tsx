import { describe, expect, it } from 'vitest';

import { appendGatewayContextHeaders } from '@/lib/gatewayContext';

describe('gateway context headers', () => {
  it('forwards only canonical request context with a normalized tenant header', () => {
    const source = new Headers({
      'x-tenant-id': ' tenant-a ',
      'x-correlation-id': ' correlation-a ',
      'x-request-id': ' request-a ',
      traceparent: ' 00-trace-a-span-a-01 ',
      'idempotency-key': ' idem-a ',
      authorization: 'Bearer browser-token',
      cookie: 'session=private',
      'x-aion-admin-token': 'untrusted-admin-token',
    });

    const result = appendGatewayContextHeaders(new Headers(), source);

    expect(Object.fromEntries(result.entries())).toEqual({
      'idempotency-key': 'idem-a',
      'tenant-id': 'tenant-a',
      traceparent: '00-trace-a-span-a-01',
      'x-correlation-id': 'correlation-a',
      'x-request-id': 'request-a',
    });
  });

  it('does not replace explicitly supplied internal context', () => {
    const target = new Headers({
      'idempotency-key': 'internal-idem',
      'tenant-id': 'internal-tenant',
    });
    const source = new Headers({
      'idempotency-key': 'browser-idem',
      'x-tenant-id': 'browser-tenant',
    });

    appendGatewayContextHeaders(target, source);

    expect(target.get('idempotency-key')).toBe('internal-idem');
    expect(target.get('tenant-id')).toBe('internal-tenant');
  });
});
