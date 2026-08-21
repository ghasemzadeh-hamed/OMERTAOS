import { NextRequest, NextResponse } from 'next/server';

import { gatewayFetch } from '@/lib/gatewayClient';
import { addAssistantMessage, addMessage, getMessages } from '@/lib/osChatStore';

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
  if (!contentText.trim()) {
    return NextResponse.json({
      ok: false,
      data: null,
      error: { code: 'EMPTY_MESSAGE', message: 'Message content is required.' },
    }, { status: 400 });
  }
  const result = addMessage(threadId, contentText);
  if (!result.ok) {
    return NextResponse.json(result, { status: 400 });
  }

  try {
    const task = await gatewayFetch('/v1/tasks', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        schemaVersion: '1.0',
        intent: 'chat',
        params: { message: contentText.trim() },
        preferredEngine: 'auto',
        priority: 'normal',
        metadata: { source: 'console-chat', threadId },
      }),
    }) as Record<string, unknown>;
    const error = task.error && typeof task.error === 'object' ? task.error as Record<string, unknown> : null;
    const taskResult = task.result;
    const responseText = typeof taskResult === 'string'
      ? taskResult
      : error && typeof error.message === 'string'
        ? error.message
        : taskResult
          ? JSON.stringify(taskResult, null, 2)
          : `Task finished with status ${String(task.status ?? 'unknown')}.`;
    addAssistantMessage(threadId, responseText, {
      runId: typeof task.taskId === 'string' ? task.taskId : undefined,
      meta: {
        status: task.status,
        engine: task.engine,
        usage: task.usage,
      },
    });
    return NextResponse.json(result);
  } catch (error) {
    const status = typeof (error as { status?: unknown }).status === 'number'
      ? (error as { status: number }).status
      : 502;
    return NextResponse.json({
      ok: false,
      data: result.data,
      error: { code: 'GATEWAY_TASK_FAILED', message: 'Gateway could not execute the chat task.' },
    }, { status });
  }
}
