import { readSettings } from './config';
import type { ServiceState } from '../types/shell';

export interface GatewayHealth {
  state: ServiceState;
  label: string;
  controlState: ServiceState;
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
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 2500);
  try {
    const response = await fetch(`${gatewayUrl.replace(/\/$/, '')}/health`, {
      signal: controller.signal,
      cache: 'no-store',
    });
    if (!response.ok) {
      throw new Error(`Gateway health returned ${response.status}`);
    }
    const payload = await response.json() as { dependencies?: { control?: string } };
    return {
      state: 'online',
      label: 'Gateway online',
      controlState: payload.dependencies?.control === 'ok' ? 'online' : 'offline',
    };
  } catch {
    return { state: 'offline', label: 'Gateway offline', controlState: 'offline' };
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function checkService(url: string, path = ''): Promise<ServiceState> {
  const online = await requestOk(`${url.replace(/\/$/, '')}${path}`);
  return online ? 'online' : 'offline';
}
