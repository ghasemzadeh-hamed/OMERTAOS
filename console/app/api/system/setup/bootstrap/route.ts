import { NextResponse } from 'next/server';
import { z } from 'zod';

import { GATEWAY_HTTP_URL } from '@/lib/gatewayConfig';

const payloadSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
  profile: z.enum(['user', 'professional', 'enterprise-vip']),
  encryptData: z.boolean().default(true),
  totpIssuer: z.string().optional(),
  webauthnRpId: z.string().optional(),
  recoveryEmail: z.string().optional(),
});

export async function POST(request: Request) {
  const json = await request.json().catch(() => ({}));
  const parsed = payloadSchema.safeParse(json);
  if (!parsed.success) {
    return NextResponse.json({ error: 'Invalid setup payload' }, { status: 400 });
  }

  const response = await fetch(`${GATEWAY_HTTP_URL}/v1/setup/bootstrap`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(parsed.data),
  });

  const text = await response.text();
  const body = text ? (() => { try { return JSON.parse(text); } catch { return { raw: text }; } })() : {};
  if (!response.ok) {
    return NextResponse.json({ error: (body as any)?.detail || (body as any)?.error || 'Failed to persist setup' }, { status: response.status });
  }
  return NextResponse.json(body);
}
