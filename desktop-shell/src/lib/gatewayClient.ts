import { readSettings } from './config';
import type { ServiceState } from '../types/shell';

export interface GatewayHealth {
  state: ServiceState;
  label: string;
}

async function requestOk(url: string, timeoutMs = 2500): Promise<boolean> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, { signal: controller.signal, cache: 'no-store' });
    return response.ok;
  } catch {
    return false;
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function getGatewayHealth(): Promise<GatewayHealth> {
  const { gatewayUrl } = readSettings();
  const online = await requestOk(`${gatewayUrl.replace(/\/$/, '')}/health`);
  return online
    ? { state: 'online', label: 'Gateway online' }
    : { state: 'offline', label: 'Gateway offline' };
}

export async function checkService(url: string, path = ''): Promise<ServiceState> {
  const online = await requestOk(`${url.replace(/\/$/, '')}${path}`);
  return online ? 'online' : 'offline';
}
