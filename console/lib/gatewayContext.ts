const CONTEXT_HEADERS = [
  'x-correlation-id',
  'x-request-id',
  'traceparent',
  'idempotency-key',
] as const;

export function appendGatewayContextHeaders(target: Headers, source: Headers): Headers {
  const tenant =
    source.get('tenant-id') || source.get('x-tenant-id') || source.get('x-tenant');
  if (tenant?.trim() && !target.has('tenant-id')) {
    target.set('tenant-id', tenant.trim());
  }

  for (const name of CONTEXT_HEADERS) {
    const value = source.get(name);
    if (value?.trim() && !target.has(name)) {
      target.set(name, value.trim());
    }
  }
  return target;
}
