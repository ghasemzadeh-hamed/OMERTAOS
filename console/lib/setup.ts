import { prisma } from '@/lib/prisma';

const SETUP_ENV_FLAG = 'AION_SETUP_COMPLETED';

export async function isSetupComplete(): Promise<boolean> {
  const flag = process.env[SETUP_ENV_FLAG];
  if (typeof flag === 'string' && flag.toLowerCase() === 'true') {
    return true;
  }

  try {
    const admins = await prisma.user.count({ where: { role: 'ADMIN' } });
    return admins > 0;
  } catch (error) {
    console.error('[console] Failed to determine setup status', error);
    return false;
  }
}

export async function getSetupStatus() {
  const setupComplete = await isSetupComplete();
  return {
    setupComplete,
  };
}
