import { NextResponse } from 'next/server';

import { getSetupStatus } from '@/lib/setup';

export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';

export async function GET() {
  const status = await getSetupStatus();
  return NextResponse.json(status);
}
