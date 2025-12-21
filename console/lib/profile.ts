import { GATEWAY_HTTP_URL } from '@/lib/gatewayConfig';
import { getConsoleSecrets } from '@/lib/serverConfig';
import { setSetupState, ensureSetupState } from '@/lib/systemState';

export type ProfileId = 'user' | 'professional' | 'enterprise-vip';

export type ProfileState = {
  profile: ProfileId | null;
  setupDone: boolean;
  updatedAt?: string;
};

class GatewayProfileError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = 'GatewayProfileError';
    this.status = status;
  }
}

const VALID_PROFILES: ProfileId[] = ['user', 'professional', 'enterprise-vip'];

const normalizeProfileId = (value: unknown): ProfileId | null => {
  if (typeof value !== 'string') {
    return null;
  }
  const lowered = value.toLowerCase();
  return VALID_PROFILES.includes(lowered as ProfileId) ? (lowered as ProfileId) : null;
};

const normalizeProfileResponse = (data: any): ProfileState => ({
  profile: normalizeProfileId(data?.profile),
  setupDone: Boolean(data?.setupDone),
  updatedAt: typeof data?.updatedAt === 'string' ? data.updatedAt : undefined,
});

export async function fetchProfileState(): Promise<ProfileState> {
  const res = await fetch(`${GATEWAY_HTTP_URL}/v1/config/profile`, { cache: 'no-store' });
  const text = await res.text();
  if (!res.ok) {
    const message = text || `Gateway responded with status ${res.status} while reading profile`;
    throw new GatewayProfileError(message, res.status);
  }
  const data = text ? (() => { try { return JSON.parse(text); } catch { return {}; } })() : {};
  const setupDone = await ensureSetupState();
  return { ...normalizeProfileResponse(data), setupDone };
}

export async function updateProfileState(
  body: { profile: string; setupDone: boolean },
): Promise<ProfileState & { ok: true }> {
  const { adminToken } = await getConsoleSecrets();
  const res = await fetch(`${GATEWAY_HTTP_URL}/v1/config/profile`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      ...(adminToken ? { authorization: `Bearer ${adminToken}` } : {}),
    },
    body: JSON.stringify(body ?? {}),
  });
  const text = await res.text();
  const data = text ? (() => { try { return JSON.parse(text); } catch { return {}; } })() : {};
  if (!res.ok) {
    const message =
      typeof (data as any)?.detail === 'string'
        ? (data as any).detail
        : typeof (data as any)?.error === 'string'
          ? (data as any).error
          : text || `Gateway responded with status ${res.status} while updating profile`;
    throw new GatewayProfileError(message, res.status);
  }
  const updatedSetup = body.setupDone ? await setSetupState(true) : await ensureSetupState();
  return { ok: true, ...normalizeProfileResponse(data), setupDone: updatedSetup };
}

export { GatewayProfileError };
