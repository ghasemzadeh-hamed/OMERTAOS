import { NextResponse } from 'next/server';

import { gatewayFetch } from '@/lib/gatewayClient';

export async function POST(request: Request) {
  try {
    const payload = await request.json().catch(() => ({}));
    const data = await gatewayFetch('/api/onboarding/submit', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload ?? {}),
    });
    return NextResponse.json(data);
  } catch (error: any) {
    const status = typeof error?.status === 'number' ? error.status : 502;
    const body = error?.body || { error: 'Unable to mark onboarding complete' };
    return NextResponse.json(body, { status });
  }
}
