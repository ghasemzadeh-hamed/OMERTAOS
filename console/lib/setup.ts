import { fetchProfileState } from '@/lib/profile';

export async function isSetupComplete(): Promise<boolean> {
  try {
    const profile = await fetchProfileState();
    return Boolean(profile.setupDone);
  } catch (error) {
    console.error('[console] Failed to determine setup status from gateway', error);
    return false;
  }
}

export async function getSetupStatus() {
  try {
    const profile = await fetchProfileState();
    return {
      setupComplete: Boolean(profile.setupDone),
      profile: profile.profile,
      updatedAt: profile.updatedAt,
    };
  } catch (error) {
    console.error('[console] Failed to read setup status', error);
    return {
      setupComplete: false,
      profile: null as string | null,
      updatedAt: undefined as string | undefined,
    };
  }
}
