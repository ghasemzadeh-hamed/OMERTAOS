import { NextRequest, NextResponse } from 'next/server';

import { GatewayProfileError, fetchProfileState, updateProfileState } from '@/lib/profile';

export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';

export async function GET() {
  try {
    const profile = await fetchProfileState();
    return NextResponse.json(profile);
  } catch (error) {
    console.error('[console] Failed to fetch profile from gateway', error);
    const status = error instanceof GatewayProfileError && error.status ? error.status : 502;
    return NextResponse.json(
      {
        error: 'Failed to fetch setup profile from gateway',
        profile: null,
        setupDone: false,
      },
      { status },
    );
  }
}

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => null);
  const profile = typeof body?.profile === 'string' ? body.profile : '';
  const setupDone = Boolean(body?.setupDone);
  if (!profile) {
    return NextResponse.json(
      { error: 'profile is required' },
      { status: 400 },
    );
  }
  try {
    const response = await updateProfileState({ profile, setupDone });
    return NextResponse.json(response);
  } catch (error) {
    console.error('[console] Failed to update profile via gateway', error);
    const status = error instanceof GatewayProfileError && error.status ? error.status : 502;
    const message = error instanceof Error ? error.message : 'Failed to update setup profile';
    return NextResponse.json({ error: message }, { status });
  }
}
