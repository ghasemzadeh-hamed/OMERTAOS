import { NextResponse } from 'next/server';

import { gatewayFetch } from '@/lib/gatewayClient';

export async function GET(_: Request, context: { params: { id: string } }) {
  try {
    const data = await gatewayFetch(`/api/agents/${context.params.id}`, { method: 'GET' });
    return NextResponse.json(data);
  } catch (error: any) {
    const status = typeof error?.status === 'number' ? error.status : 502;
    return NextResponse.json({ error: 'Unable to load agent', details: error?.body }, { status });
  }
}
