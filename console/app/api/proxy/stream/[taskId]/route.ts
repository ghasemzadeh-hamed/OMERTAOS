import { NextRequest } from 'next/server';

const base = process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:3000';

export async function GET(request: NextRequest, { params }: { params: { taskId: string } }) {
  const response = await fetch(`${base}/v1/stream/${params.taskId}`, {
    headers: request.headers,
  });
  const stream = response.body;
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    },
  });
}
