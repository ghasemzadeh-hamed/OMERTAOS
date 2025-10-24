import { NextResponse } from 'next/server';
import { publishTaskUpdate } from '@/lib/realtime';

export async function POST(request: Request) {
  const body = await request.json();
  publishTaskUpdate(body);
  return NextResponse.json({ received: true });
}
