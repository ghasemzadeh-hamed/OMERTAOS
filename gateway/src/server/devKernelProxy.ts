import type { FastifyRequest } from 'fastify';
import { gatewayConfig } from '../config.js';
import type {
  DevKernelRequest,
  DevKernelResponse,
  TaskRequest,
} from '../types.js';

const DEV_MODE_HEADER = 'x-aion-mode';
const DEV_PROFILE_HEADER = 'x-aion-kernel-profile';

export const devKernelEnabled = () => gatewayConfig.devKernel.enabled;

export const shouldUseDevKernel = (request: FastifyRequest): boolean => {
  if (!devKernelEnabled()) {
    return false;
  }
  const headerMode = request.headers[DEV_MODE_HEADER];
  if (typeof headerMode === 'string' && headerMode.toLowerCase() === 'dev') {
    return true;
  }
  const profileHeader = request.headers[DEV_PROFILE_HEADER];
  if (
    typeof profileHeader === 'string' &&
    profileHeader.toLowerCase() === gatewayConfig.devKernel.profile.toLowerCase()
  ) {
    return true;
  }
  return false;
};

const serializeTaskRequest = (task: TaskRequest): DevKernelRequest => {
  const summary: string[] = [task.intent];
  if (Object.keys(task.params ?? {}).length > 0) {
    summary.push('');
    summary.push('Parameters:');
    summary.push(JSON.stringify(task.params, null, 2));
  }
  return {
    message: summary.join('\n'),
    metadata: {
      schemaVersion: task.schemaVersion,
      preferredEngine: task.preferredEngine,
      priority: task.priority,
      metadata: task.metadata ?? {},
    },
  };
};

export const buildDevKernelPayload = (
  task: TaskRequest,
  request: FastifyRequest,
): DevKernelRequest => {
  const payload = serializeTaskRequest(task);
  const headers: Record<string, unknown> = {};
  if (request.headers['x-request-id']) {
    headers['x-request-id'] = request.headers['x-request-id'];
  }
  if (request.headers['x-correlation-id']) {
    headers['x-correlation-id'] = request.headers['x-correlation-id'];
  }
  if (Object.keys(headers).length > 0) {
    payload.metadata = {
      ...(payload.metadata ?? {}),
      headers,
    };
  }
  return payload;
};

type FetchLikeResponse = {
  ok: boolean;
  status: number;
  text: () => Promise<string>;
  json: () => Promise<unknown>;
};

type FetchLike = (input: string, init?: Record<string, unknown>) => Promise<FetchLikeResponse>;

const resolveFetch = (): FetchLike => {
  const candidate = (globalThis as { fetch?: unknown }).fetch;
  if (typeof candidate !== 'function') {
    throw new Error('Fetch API is not available in this environment');
  }
  return candidate as FetchLike;
};

export const callDevKernel = async (
  payload: DevKernelRequest,
): Promise<DevKernelResponse> => {
  const httpFetch = resolveFetch();
  const response = await httpFetch(gatewayConfig.devKernel.url, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-aion-kernel-profile': gatewayConfig.devKernel.profile,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Dev kernel request failed: ${response.status} ${text}`);
  }

  const body = (await response.json()) as DevKernelResponse;
  return body;
};
