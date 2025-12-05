import { GATEWAY_HTTP_URL } from '@/lib/gatewayConfig';
import { getConsoleSecrets } from '@/lib/serverConfig';

export type ProfileState = {
  profile: string | null;
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

const normalizeProfileResponse = (data: any): ProfileState => ({
  profile: typeof data?.profile === 'string' ? data.profile : null,
  setupDone: Boolean(data?.setupDone),
  updatedAt: typeof data?.updatedAt === 'string' ? data.updatedAt : undefined,
});

export async function fetchProfileState(): Promise<ProfileState> {
  const res = await fetch(`${GATEWAY_HTTP_URL}/v1/config/profile`, { cache: 'no-store' });
  if (!res.ok) {
    const detail = await res.text();
    throw new GatewayProfileError(
      detail || `Gateway responded with status ${res.status} while reading profile`,
      res.status,
    );
  }
  const data = await res.json();
  return normalizeProfileResponse(data);
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
  return { ok: true, ...normalizeProfileResponse(data) };
}

export { GatewayProfileError };
