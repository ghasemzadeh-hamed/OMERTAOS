export type BootstrapState = {
  setupDone: boolean;
  onboardingComplete: boolean;
  authenticated: boolean;
  setupUnknown?: boolean;
  role?: 'user' | 'admin';
  tenantId?: string;
  profile?: 'user' | 'professional' | 'enterprise-vip' | null;
};

function resolveBaseUrl(baseUrl?: string) {
  if (baseUrl) return baseUrl;
  if (process.env.NEXTAUTH_URL) return process.env.NEXTAUTH_URL;
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return 'http://localhost:3001';
}

export async function resolveBootstrapState(baseUrl?: string): Promise<BootstrapState> {
  const origin = resolveBaseUrl(baseUrl);
  const res = await fetch(`${origin}/api/system/bootstrap`, { cache: 'no-store' }).catch(() => null);
  if (!res?.ok) {
    return { setupDone: false, onboardingComplete: false, authenticated: false, setupUnknown: true };
  }
  const data = (await res.json()) as BootstrapState;
  return {
    setupDone: Boolean(data.setupDone),
    onboardingComplete: Boolean(data.onboardingComplete),
    authenticated: Boolean(data.authenticated),
    setupUnknown: Boolean(data.setupUnknown),
    role: data.role,
    tenantId: data.tenantId,
    profile: data.profile,
  };
}
