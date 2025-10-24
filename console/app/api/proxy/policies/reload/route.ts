import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../../../lib/auth';

const controlBase = process.env.NEXT_PUBLIC_CONTROL_URL ?? 'http://localhost:8081';

export async function POST() {
  const session = await getServerSession(authOptions);
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (session?.user?.tenantId) {
    headers['X-Tenant'] = String(session.user.tenantId);
  }
  if (session?.accessToken) {
    headers['Authorization'] = `Bearer ${session.accessToken}`;
  }
  const response = await fetch(`${controlBase}/v1/router/policy/reload`, {
    method: 'POST',
    headers,
  });
  const data = await response.json().catch(() => ({}));
  return NextResponse.json(data, { status: response.status });
}
