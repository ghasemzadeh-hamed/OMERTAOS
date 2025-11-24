export const dynamic = 'force-dynamic';
export const revalidate = 0;

const base = process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:8080';

export async function GET() {
  if (process.env.NEXT_PHASE === 'phase-production-build') {
    return new Response('Control stream unavailable', { status: 503 });
  }

  try {
    const response = await fetch(`${base}/v1/logs/stream`);
    if (!response.ok || !response.body) {
      return new Response('Control stream unavailable', { status: 502 });
    }

    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
    });
  } catch (error) {
    console.error('Failed to proxy control stream', error);
    return new Response('Control stream unavailable', { status: 503 });
  }
}
