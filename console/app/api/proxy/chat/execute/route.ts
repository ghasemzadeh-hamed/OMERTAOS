import { NextRequest, NextResponse } from 'next/server';
import { withGatewayAuth } from '../../../../../lib/api';

export async function POST(request: NextRequest) {
  const body = await request.json();
  const response = await withGatewayAuth('/v1/chat/execute', {
    method: 'POST',
    body: JSON.stringify(body),
  });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}
