import { prisma } from '@/lib/prisma';

const SETUP_STATE_KEY = 'setup_completed';

export const readSetupState = async () => {
  const record = await prisma.systemState.findUnique({ where: { key: SETUP_STATE_KEY } });
  return Boolean(record?.boolValue);
};

export const ensureSetupState = async () => {
  const record = await prisma.systemState.upsert({
    where: { key: SETUP_STATE_KEY },
    update: {},
    create: { key: SETUP_STATE_KEY, boolValue: false },
  });
  return Boolean(record.boolValue);
};

export const setSetupState = async (completed: boolean) => {
  const record = await prisma.systemState.upsert({
    where: { key: SETUP_STATE_KEY },
    update: { boolValue: completed },
    create: { key: SETUP_STATE_KEY, boolValue: completed },
  });
  return Boolean(record.boolValue);
};
