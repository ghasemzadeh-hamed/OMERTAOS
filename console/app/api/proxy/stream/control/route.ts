const base = process.env.NEXT_PUBLIC_CONTROL_URL ?? 'http://localhost:9000';

export async function GET() {
  const response = await fetch(`${base}/v1/logs/stream`);
  return new Response(response.body, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    },
  });
}
