import { NextRequest } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../../lib/auth';

const base = process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:8080';
const consoleApiKey = process.env.CONSOLE_GATEWAY_API_KEY ?? process.env.AION_CONSOLE_GATEWAY_API_KEY;

export async function GET(request: NextRequest, { params }: { params: { taskId: string } }) {
  const session = await getServerSession(authOptions);
  const headers = new Headers();
  if (consoleApiKey) {
    headers.set('X-API-Key', consoleApiKey);
  }
  if (session?.user?.tenantId) {
    headers.set('X-Tenant', String(session.user.tenantId));
  }
  if (session?.accessToken) {
    headers.set('Authorization', `Bearer ${session.accessToken}`);
  }
  const response = await fetch(`${base}/v1/stream/${params.taskId}`, {
    headers,
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
