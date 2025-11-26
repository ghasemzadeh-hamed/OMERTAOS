import { NextResponse } from 'next/server';

import { prisma } from '@/lib/prisma';

export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';

export async function GET() {
  try {
    await prisma.$queryRaw`SELECT 1`;
    return NextResponse.json({ status: 'ok', service: 'console', database: 'ok' });
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('[console] Dashboard health check failed', error);
    return NextResponse.json({ status: 'degraded', service: 'console', database: 'unavailable' });
  }
}
