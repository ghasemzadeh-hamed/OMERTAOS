import { NextRequest, NextResponse } from 'next/server';

import { getBootstrapState } from '@/lib/bootstrap';

export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';

export async function GET(_request: NextRequest) {
  const state = await getBootstrapState();
  return NextResponse.json(state);
}
