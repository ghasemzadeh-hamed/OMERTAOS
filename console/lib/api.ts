import { headers } from 'next/headers';
import { NextResponse } from 'next/server';
import { Task } from '../types';

const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8080';

async function jsonFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function withGatewayAuth(path: string, init?: RequestInit) {
  const apiKey = process.env.NEXT_PUBLIC_CONSOLE_GATEWAY_KEY || process.env.AION_CONSOLE_GATEWAY_API_KEY;
  const tenant = headers().get('x-tenant') || undefined;
  return fetch(`${GATEWAY_URL}${path}`, {
    ...init,
    headers: {
      'content-type': 'application/json',
      ...(apiKey ? { 'x-api-key': apiKey } : {}),
      ...(tenant ? { 'x-tenant': tenant } : {}),
      ...(init?.headers || {}),
    },
  });
}

export function createSseProxyResponse(path: string) {
  const apiKey = process.env.NEXT_PUBLIC_CONSOLE_GATEWAY_KEY || process.env.AION_CONSOLE_GATEWAY_API_KEY;
  const tenant = headers().get('x-tenant') || undefined;
  const target = `${GATEWAY_URL}${path}`;
  const stream = new ReadableStream({
    async start(controller) {
      const response = await fetch(target, {
        headers: {
          ...(apiKey ? { 'x-api-key': apiKey } : {}),
          ...(tenant ? { 'x-tenant': tenant } : {}),
        },
      });
      if (!response.body) {
        controller.close();
        return;
      }
      const reader = response.body.getReader();
      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          break;
        }
        controller.enqueue(value);
      }
      controller.close();
    },
  });
  return new NextResponse(stream, {
    headers: {
      'content-type': 'text/event-stream',
      'cache-control': 'no-cache',
      connection: 'keep-alive',
    },
  });
}

const normalizeTask = (payload: any): Task => ({
  taskId: payload.task_id ?? payload.taskId,
  intent: payload.intent,
  params: payload.params ?? {},
  status: payload.status,
  result: payload.result,
  createdAt: payload.created_at ? new Date(payload.created_at * 1000).toISOString() : undefined,
  updatedAt: payload.updated_at ? new Date(payload.updated_at * 1000).toISOString() : undefined,
  tenantId: payload.tenant_id ?? payload.tenantId,
});

export async function listTasks(): Promise<Task[]> {
  const data = await jsonFetch<any[]>('/api/proxy/tasks');
  return data.map(normalizeTask);
}

export async function createTask(payload: Partial<Task>): Promise<Task> {
  const result = await jsonFetch<any>('/api/proxy/tasks', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return normalizeTask(result);
}

export async function fetchPolicy(): Promise<Record<string, unknown>> {
  return jsonFetch('/api/proxy/policies');
}

export async function updatePolicy(policy: Record<string, unknown>) {
  return jsonFetch('/api/proxy/policies', {
    method: 'PUT',
    body: JSON.stringify(policy),
  });
}

export async function reloadRouterPolicy() {
  return jsonFetch('/api/proxy/policies/reload', { method: 'POST' });
}
