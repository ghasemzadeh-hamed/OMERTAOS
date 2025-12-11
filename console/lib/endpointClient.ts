'use client';

import { Capability, CapabilityEndpoint, loadCapabilities } from './schemaLoader';

type CallOptions = {
  payload?: any;
  tenantId?: string;
  params?: Record<string, string>;
  cache?: RequestCache;
};

function substitutePath(path: string, params?: Record<string, string>): string {
  if (!params) return path;
  let finalPath = path;
  for (const [key, value] of Object.entries(params)) {
    finalPath = finalPath.replace(`{${key}}`, encodeURIComponent(value));
  }
  return finalPath;
}

async function resolveEndpoint(endpointRef: string): Promise<CapabilityEndpoint | null> {
  const [service, method, rawPath] = endpointRef.split(':');
  if (!service || !method || !rawPath) return null;
  return { service: service as CapabilityEndpoint['service'], method, path: rawPath };
}

function baseUrlForService(service: string): string {
  switch (service) {
    case 'gateway':
      return process.env.NEXT_PUBLIC_GATEWAY_URL ?? '';
    case 'control':
      return process.env.NEXT_PUBLIC_CONTROL_URL ?? '';
    default:
      return '';
  }
}

export async function callEndpoint(endpointRef: string, options: CallOptions = {}) {
  const endpoint = await resolveEndpoint(endpointRef);
  if (!endpoint) throw new Error(`Unknown endpointRef ${endpointRef}`);

  const url = `${baseUrlForService(endpoint.service)}${substitutePath(endpoint.path, options.params)}`;
  const headers: HeadersInit = { 'content-type': 'application/json' };
  if (options.tenantId) {
    headers['tenant-id'] = options.tenantId;
  }

  const res = await fetch(url, {
    method: endpoint.method,
    headers,
    body: endpoint.method !== 'GET' ? JSON.stringify(options.payload ?? {}) : undefined,
    cache: options.cache ?? 'no-store'
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const message = typeof data?.error === 'string' ? data.error : 'Request failed';
    throw new Error(message);
  }
  return data;
}

export async function getEndpointForCapability(capabilityId: string, matcher: (endpoint: CapabilityEndpoint) => boolean): Promise<string | null> {
  const capabilities: Capability[] = await loadCapabilities();
  const capability = capabilities.find((c) => c.id === capabilityId);
  if (!capability) return null;
  const target = capability.endpoints.find(matcher);
  return target ? `${target.service}:${target.method}:${target.path}` : null;
}
