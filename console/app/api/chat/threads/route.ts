import { NextRequest, NextResponse } from 'next/server';

import { createThread, listThreads } from '@/lib/osChatStore';

export function GET() {
  const result = listThreads();
  return NextResponse.json(result);
}

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));
  const title = typeof body?.title === 'string' ? body.title : '';
  const result = createThread(title);
  return NextResponse.json(result, { status: result.ok ? 200 : 400 });
}
