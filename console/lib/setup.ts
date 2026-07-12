import { ensureSetupState, readSetupState, setSetupState } from '@/lib/systemState';

export async function isSetupComplete(): Promise<boolean> {
  try {
    return await ensureSetupState();
  } catch (error) {
    console.error('[console] Failed to determine setup status from persistence layer', error);
    return false;
  }
}

export async function getSetupStatus() {
  try {
    const setupComplete = await readSetupState();
    return { setupComplete, profile: null as string | null, updatedAt: undefined as string | undefined };
  } catch (error) {
    console.error('[console] Failed to read setup status', error);
    return {
      setupComplete: false,
      profile: null as string | null,
      updatedAt: undefined as string | undefined,
    };
  }
}

export async function completeSetup() {
  return setSetupState(true);
}
