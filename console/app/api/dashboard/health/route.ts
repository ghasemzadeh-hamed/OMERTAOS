import { NextResponse } from 'next/server';

import { prisma } from '@/lib/prisma';
import { getSetupStatus } from '@/lib/setup';

const gatewayUrl =
  process.env.NEXT_PUBLIC_GATEWAY_URL ||
  process.env.GATEWAY_BASE_URL ||
  'http://localhost:3000';

type ServiceStatus = 'ok' | 'degraded' | 'error' | 'unknown';

const ok = <T>(details: T): { status: ServiceStatus; details: T } => ({
  status: 'ok',
  details,
});

const degraded = <T>(details: T): { status: ServiceStatus; details: T } => ({
  status: 'degraded',
  details,
});

export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';

async function checkDatabase() {
  try {
    await prisma.$queryRaw`SELECT 1`;
    return ok('Connected');
  } catch (error) {
    console.error('[console] Dashboard health check failed', error);
    return degraded('Database unavailable');
  }
}

async function checkHttpService(url: string) {
  try {
    const res = await fetch(url, { cache: 'no-store' });
    if (res.ok) return ok(`Reachable at ${url}`);
    return degraded(`Responded with status ${res.status}`);
  } catch (error) {
    console.error(`[console] Failed to reach ${url}`, error);
    return degraded('Unreachable');
  }
}

export async function GET() {
  const [db, gateway, setup] = await Promise.all([
    checkDatabase(),
    checkHttpService(`${gatewayUrl}/healthz`),
    getSetupStatus(),
  ]);

  const services = {
    postgres: db,
    gateway,
  } as Record<string, { status: ServiceStatus; details: string }>;

  const overallStatus: ServiceStatus = [db.status, gateway.status].some((s) => s === 'error')
    ? 'error'
    : [db.status, gateway.status].some((s) => s === 'degraded')
      ? 'degraded'
      : 'ok';

  return NextResponse.json({
    status: overallStatus,
    services,
    setupComplete: setup.setupComplete,
    profile: setup.profile,
  });
}
