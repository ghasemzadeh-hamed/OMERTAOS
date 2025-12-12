import { NextResponse } from 'next/server';

import { gatewayFetch } from '@/lib/gatewayClient';

export async function GET() {
  try {
    const data = await gatewayFetch('/api/onboarding/status', { method: 'GET' });
    return NextResponse.json(data);
  } catch (error: any) {
    const status = typeof error?.status === 'number' ? error.status : 502;
    const body = error?.body || { error: 'Unable to read onboarding status' };
    return NextResponse.json(body, { status });
  }
}
