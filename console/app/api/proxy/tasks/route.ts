import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { randomUUID } from 'node:crypto';
import { authOptions } from '../../../lib/auth';

const base = process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:8080';
const consoleApiKey = process.env.CONSOLE_GATEWAY_API_KEY ?? process.env.AION_CONSOLE_GATEWAY_API_KEY;

const buildHeaders = async (extra?: HeadersInit) => {
  const session = await getServerSession(authOptions);
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (consoleApiKey) {
    headers['X-API-Key'] = consoleApiKey;
  }
  if (session?.user?.tenantId) {
    headers['X-Tenant'] = String(session.user.tenantId);
  }
  if (session?.accessToken) {
    headers['Authorization'] = `Bearer ${session.accessToken}`;
  }
  return { ...headers, ...(extra as Record<string, string>) };
};

export async function GET(request: Request) {
  const url = new URL(request.url);
  const id = url.searchParams.get('id');
  const headers = await buildHeaders();
  if (id) {
    const response = await fetch(`${base}/v1/tasks/${id}`, { headers });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  }
  const controlBase = process.env.NEXT_PUBLIC_CONTROL_URL ?? 'http://localhost:8081';
  const response = await fetch(`${controlBase}/v1/tasks`, { headers });
  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}

export async function POST(request: Request) {
  const body = await request.json();
  const headers = await buildHeaders({ 'Idempotency-Key': randomUUID() });
  const response = await fetch(`${base}/v1/tasks`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });
  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
