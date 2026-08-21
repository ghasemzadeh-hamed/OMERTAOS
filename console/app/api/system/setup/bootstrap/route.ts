import { NextResponse } from 'next/server';
import bcrypt from 'bcrypt';
import { z } from 'zod';

import { GATEWAY_HTTP_URL } from '@/lib/gatewayConfig';
import { prisma } from '@/lib/prisma';
import { completeSetup } from '@/lib/setup';

const payloadSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
  profile: z.enum(['user', 'professional', 'enterprise-vip']),
  encryptData: z.boolean().default(true),
  totpIssuer: z.string().optional(),
  webauthnRpId: z.string().optional(),
  recoveryEmail: z.string().optional(),
});

function adminEmailFromSetupUsername(username: string) {
  const normalized = username.trim().toLowerCase();
  return normalized.includes('@') ? normalized : `${normalized}@local`;
}

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

  const passwordHash = await bcrypt.hash(parsed.data.password, 12);
  await prisma.user.upsert({
    where: { email: adminEmailFromSetupUsername(parsed.data.username) },
    update: {
      password: passwordHash,
      role: 'ADMIN',
      name: parsed.data.username.trim(),
    },
    create: {
      email: adminEmailFromSetupUsername(parsed.data.username),
      password: passwordHash,
      role: 'ADMIN',
      name: parsed.data.username.trim(),
    },
  });
  await completeSetup();

  return NextResponse.json(body);
}
