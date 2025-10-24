import { NextResponse } from 'next/server';

const base = process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:8080';

export async function GET() {
  const response = await fetch(`${base}/v1/tasks`, { credentials: 'include' });
  const data = await response.json();
  return NextResponse.json(data);
}

export async function POST(request: Request) {
  const body = await request.json();
  const response = await fetch(`${base}/v1/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    credentials: 'include',
  });
  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
