import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

import { GatewayProfileError, fetchProfileState, updateProfileState } from '@/lib/profile';

export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';

const bodySchema = z.object({
  profile: z.enum(['user', 'professional', 'enterprise-vip']),
  setupDone: z.boolean().optional(),
});

export async function GET() {
  try {
    const profile = await fetchProfileState();
    return NextResponse.json(profile);
  } catch (error) {
    console.error('[console] Failed to fetch profile from gateway', error);
    const status = error instanceof GatewayProfileError && error.status ? error.status : 502;
    const message =
      error instanceof GatewayProfileError ? error.message : 'Failed to fetch setup profile from gateway';
    const hint =
      process.env.NODE_ENV !== 'production'
        ? `Gateway returned ${status} for /v1/config/profile. In dev you may need to allow setup routes without JWT.`
        : undefined;
    return NextResponse.json(
      {
        error: message,
        hint,
        profile: null,
        setupDone: false,
      },
      { status },
    );
  }
}

export async function POST(request: NextRequest) {
  const json = await request.json().catch(() => null);
  const parsed = bodySchema.safeParse(json);
  if (!parsed.success) {
    return NextResponse.json({ error: 'profile is required' }, { status: 400 });
  }

  const payload = {
    profile: parsed.data.profile,
    setupDone: parsed.data.setupDone ?? true,
  };

  try {
    const response = await updateProfileState(payload);
    return NextResponse.json(response);
  } catch (error) {
    console.error('[console] Failed to update profile via gateway', error);
    const status = error instanceof GatewayProfileError && error.status ? error.status : 502;
    const message = error instanceof Error ? error.message : 'Failed to update setup profile';
    const hint =
      process.env.NODE_ENV !== 'production'
        ? `Gateway returned ${status} for /v1/config/profile. In dev ensure auth bypass is enabled for setup.`
        : undefined;
    return NextResponse.json({ error: message, hint }, { status });
  }
}
