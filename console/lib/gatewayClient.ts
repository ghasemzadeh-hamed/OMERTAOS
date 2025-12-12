import { cookies, headers } from 'next/headers';

import { GATEWAY_HTTP_URL } from '@/lib/gatewayConfig';

const DEFAULT_GATEWAY = 'http://localhost:3000';

export function resolveGatewayBase() {
  return GATEWAY_HTTP_URL || DEFAULT_GATEWAY;
}

export function buildGatewayHeaders(initHeaders?: HeadersInit) {
  const result = new Headers(initHeaders ?? {});
  const hdrs = headers();
  const tenantHeader = hdrs.get('x-tenant-id') || hdrs.get('tenant-id');
  if (tenantHeader) {
    result.set('tenant-id', tenantHeader);
  }

  const token = cookies().get('access_token')?.value;
  if (token && !result.has('authorization')) {
    result.set('authorization', `Bearer ${token}`);
  }

  return result;
}

export async function gatewayFetch(path: string, init?: RequestInit) {
  const url = `${resolveGatewayBase()}${path}`;
  const headers = buildGatewayHeaders(init?.headers);
  const response = await fetch(url, {
    ...init,
    headers,
    cache: init?.cache ?? 'no-store',
  });

  const text = await response.text();
  const isJson = (response.headers.get('content-type') || '').includes('application/json');
  const body = isJson ? safeJson(text) : text;

  if (!response.ok) {
    const error = new Error(`Gateway error ${response.status}`);
    (error as any).status = response.status;
    (error as any).body = body;
    throw error;
  }

  return body;
}

function safeJson(payload: string) {
  try {
    return JSON.parse(payload);
  } catch {
    return { raw: payload };
  }
}
