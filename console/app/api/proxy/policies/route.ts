import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../../lib/auth';

const controlBase = process.env.NEXT_PUBLIC_CONTROL_URL ?? 'http://localhost:8081';

async function buildHeaders() {
  const session = await getServerSession(authOptions);
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (session?.user?.tenantId) {
    headers['X-Tenant'] = String(session.user.tenantId);
  }
  if (session?.accessToken) {
    headers['Authorization'] = `Bearer ${session.accessToken}`;
  }
  return headers;
}

export async function GET() {
  const headers = await buildHeaders();
  const response = await fetch(`${controlBase}/v1/policies`, { headers });
  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}

export async function PUT(request: Request) {
  const headers = await buildHeaders();
  const body = await request.text();
  const response = await fetch(`${controlBase}/v1/policies`, {
    method: 'PUT',
    headers,
    body,
  });
  const data = await response.json().catch(() => ({}));
  return NextResponse.json(data, { status: response.status });
}
