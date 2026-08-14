import { Task } from '../types';

const gatewayBase =
  process.env.NEXT_PUBLIC_GATEWAY_URL ?? process.env.GATEWAY_BASE_URL ?? 'http://localhost:3000';

async function jsonFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function listTasks(): Promise<Task[]> {
  return jsonFetch<Task[]>(`${gatewayBase}/v1/tasks`);
}

export async function createTask(payload: Partial<Task>): Promise<Task> {
  return jsonFetch<Task>(`${gatewayBase}/v1/tasks`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchPolicy(): Promise<Record<string, unknown>> {
  return jsonFetch(`${gatewayBase}/v1/policies`);
}

export async function updatePolicy(policy: Record<string, unknown>) {
  return jsonFetch(`${gatewayBase}/v1/policies`, {
    method: 'PUT',
    body: JSON.stringify(policy),
  });
}

export async function reloadRouterPolicy() {
  return jsonFetch(`${gatewayBase}/v1/router/policy/reload`, { method: 'POST' });
}
