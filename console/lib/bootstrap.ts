import { headers } from 'next/headers';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { gatewayFetch } from '@/lib/gatewayClient';
import { fetchProfileState, ProfileId } from '@/lib/profile';

export type BootstrapState = {
  setupDone: boolean;
  onboardingComplete: boolean;
  authenticated: boolean;
  setupUnknown: boolean;
  role: 'user' | 'admin';
  tenantId?: string;
  profile?: ProfileId | null;
};

const resolveTenantId = () => {
  const hdrs = headers();
  return hdrs.get('tenant-id') || hdrs.get('x-tenant-id') || undefined;
};

const normalizeRole = (value: any): 'user' | 'admin' => {
  if (typeof value !== 'string') return 'user';
  return value.toLowerCase() === 'admin' ? 'admin' : 'user';
};

export async function getBootstrapState(): Promise<BootstrapState> {
  let setupDone = false;
  let onboardingComplete = false;
  let authenticated = false;
  let setupUnknown = false;
  let profile: ProfileId | null = null;
  let role: 'user' | 'admin' = 'user';
  const tenantId = resolveTenantId();

  try {
    const profileState = await fetchProfileState();
    setupDone = Boolean(profileState?.setupDone);
    profile = profileState.profile;
  } catch (error) {
    console.error('[console] Failed to fetch profile state', error);
    setupUnknown = true;
  }

  try {
    const session = await getServerSession(authOptions);
    authenticated = Boolean(session);
    role = normalizeRole((session as any)?.user?.role || (session as any)?.role);
  } catch (error) {
    console.error('[console] Failed to read session', error);
    authenticated = false;
  }

  if (setupDone) {
    try {
      const res = await gatewayFetch('/api/onboarding/status', { method: 'GET' });
      onboardingComplete = Boolean((res as any)?.onboardingComplete ?? (res as any)?.data?.onboardingComplete);
    } catch (error) {
      console.error('[console] Failed to read onboarding status', error);
      onboardingComplete = false;
    }
  }

  return { setupDone, onboardingComplete, authenticated, setupUnknown, role, tenantId, profile };
}
