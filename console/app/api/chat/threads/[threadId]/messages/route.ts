import { NextRequest, NextResponse } from 'next/server';

import { addMessage, getMessages } from '@/lib/osChatStore';

interface RouteContext {
  params: Promise<{ threadId: string }>;
}

export async function GET(_request: NextRequest, context: RouteContext) {
  const { threadId } = await context.params;
  const result = getMessages(threadId);
  return NextResponse.json(result);
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { threadId } = await context.params;
  const body = await request.json().catch(() => ({}));
  const contentText = typeof body?.contentText === 'string' ? body.contentText : '';
  const result = addMessage(threadId, contentText);
  return NextResponse.json(result, { status: result.ok ? 200 : 400 });
}
