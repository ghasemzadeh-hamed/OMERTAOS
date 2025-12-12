import { NextResponse } from 'next/server';

import { resolveGatewayBase } from '@/lib/gatewayClient';

const controlBase = () => process.env.NEXT_PUBLIC_CONTROL_URL || process.env.CONTROL_URL || 'http://localhost:8000';
const consoleBase = () => process.env.NEXTAUTH_URL || 'http://localhost:3001';

async function check(url: string) {
  try {
    const res = await fetch(url, { cache: 'no-store' });
    return { status: res.ok ? 'ok' : 'degraded', details: `HTTP ${res.status}` };
  } catch (error) {
    return { status: 'degraded', details: 'unreachable' };
  }
}

export async function GET() {
  const [gateway, control, consoleSvc] = await Promise.all([
    check(`${resolveGatewayBase()}/healthz`),
    check(`${controlBase()}/healthz`),
    check(`${consoleBase()}/healthz`),
  ]);

  const status = [gateway, control].some((s) => s.status === 'degraded') ? 'degraded' : 'ok';

  return NextResponse.json({
    status,
    services: {
      gateway,
      control,
      console: consoleSvc,
    },
    updatedAt: new Date().toISOString(),
  });
}
