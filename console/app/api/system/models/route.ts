import { NextResponse } from 'next/server';

import { gatewayFetch } from '@/lib/gatewayClient';

export async function GET() {
  try {
    const data = await gatewayFetch('/v1/models', { method: 'GET' });
    return NextResponse.json(data);
  } catch (error: any) {
    const status = typeof error?.status === 'number' ? error.status : 502;
    return NextResponse.json({ error: 'Unable to load models', details: error?.body }, { status });
  }
}
