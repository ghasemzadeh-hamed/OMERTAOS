import { NextRequest, NextResponse } from 'next/server';

const gatewayBase = process.env.NEXT_PUBLIC_GATEWAY_BASE ?? 'http://localhost:8080';
const adminToken = process.env.AION_SETUP_TOKEN ?? process.env.NEXT_PUBLIC_SETUP_TOKEN ?? '';

export async function GET() {
  try {
    const res = await fetch(`${gatewayBase}/v1/config/profile`, { cache: 'no-store' });
    if (!res.ok) {
      return NextResponse.json({ profile: 'user', setupDone: false }, { status: 200 });
    }
    const data = await res.json();
    return NextResponse.json({
      profile: typeof data.profile === 'string' ? data.profile : 'user',
      setupDone: Boolean(data.setupDone),
    });
  } catch (error) {
    console.error('Failed to fetch profile', error);
    return NextResponse.json({ profile: 'user', setupDone: false }, { status: 200 });
  }
}

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));
  try {
    const res = await fetch(`${gatewayBase}/v1/config/profile`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        ...(adminToken ? { authorization: `Bearer ${adminToken}` } : {}),
      },
      body: JSON.stringify(body ?? {}),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      return NextResponse.json(
        { error: data.detail || data.error || 'Failed to update profile' },
        { status: res.status || 400 },
      );
    }
    return NextResponse.json({ ok: true, profile: data.profile, setupDone: data.setupDone });
  } catch (error) {
    console.error('Failed to update profile', error);
    return NextResponse.json({ error: 'Failed to update profile' }, { status: 500 });
  }
}
