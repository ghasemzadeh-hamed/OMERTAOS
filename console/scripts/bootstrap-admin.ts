import bcrypt from 'bcrypt';
import { PrismaClient, Role } from '@prisma/client';

const prisma = new PrismaClient({ log: ['warn', 'error'] });

const normalizeBoolean = (value: string | undefined) => {
  if (!value) return false;
  const normalised = value.trim().toLowerCase();
  return ['1', 'true', 'yes', 'on'].includes(normalised);
};

const resolveAdminCredentials = () => {
  const email = process.env.CONSOLE_ADMIN_EMAIL || process.env.DEV_ADMIN_EMAIL || 'admin@local';
  const password = process.env.CONSOLE_ADMIN_PASSWORD || process.env.DEV_ADMIN_PASSWORD || 'admin123';
  const name = process.env.CONSOLE_ADMIN_NAME || 'Console Admin';
  return { email, password, name };
};

const ensureSetupState = async () => {
  await prisma.systemState.upsert({
    where: { key: 'setup_completed' },
    update: {},
    create: { key: 'setup_completed', boolValue: false },
  });
};

const ensureAdminUser = async () => {
  if (normalizeBoolean(process.env.SKIP_CONSOLE_SEED)) {
    console.info('[console] Skipping console seed because SKIP_CONSOLE_SEED is set.');
    return;
  }

  const userCount = await prisma.user.count();
  if (userCount > 0) {
    return;
  }

  const { email, password, name } = resolveAdminCredentials();
  const passwordHash = await bcrypt.hash(password, 12);

  await prisma.user.create({
    data: { email, password: passwordHash, role: Role.ADMIN, name },
  });

  console.info(`[console] Created initial admin user ${email}`);
};

export async function bootstrapConsole() {
  if (!process.env.DATABASE_URL) {
    throw new Error('[console] DATABASE_URL must be set before bootstrapping.');
  }
  await ensureSetupState();
  await ensureAdminUser();
}

if (require.main === module) {
  bootstrapConsole()
    .then(() => prisma.$disconnect())
    .catch(async (error) => {
      console.error('[console] Failed to bootstrap console', error);
      await prisma.$disconnect();
      process.exit(1);
    });
}
