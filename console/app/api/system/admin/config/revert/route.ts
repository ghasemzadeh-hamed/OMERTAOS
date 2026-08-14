import { NextResponse } from 'next/server';

import { gatewayFetch } from '@/lib/gatewayClient';

export async function POST(request: Request) {
  try {
    const payload = await request.json().catch(() => ({}));
    const data = await gatewayFetch('/v1/config/revert', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload ?? {}),
    });
    return NextResponse.json(data);
  } catch (error: any) {
    const status = typeof error?.status === 'number' ? error.status : 502;
    return NextResponse.json({ error: 'Unable to revert config change', details: error?.body }, { status });
  }
}
