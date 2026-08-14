import bcrypt from 'bcrypt';
import { PrismaClient, Role } from '@prisma/client';

export const prisma = new PrismaClient({ log: ['warn', 'error'] });

const normalizeBoolean = (value: string | undefined) => {
  if (!value) return false;
  const normalised = value.trim().toLowerCase();
  return ['1', 'true', 'yes', 'on'].includes(normalised);
};

export const resolveAdminCredentials = () => {
  const email = process.env.CONSOLE_ADMIN_EMAIL?.trim();
  const password = process.env.CONSOLE_ADMIN_PASSWORD;
  const name = process.env.CONSOLE_ADMIN_NAME || 'Console Admin';
  if (!email || !email.includes('@')) {
    throw new Error('[console] CONSOLE_ADMIN_EMAIL must be an explicit email address.');
  }
  if (!password || password.length < 16 || password === 'admin123') {
    throw new Error('[console] CONSOLE_ADMIN_PASSWORD must be an explicit non-default value of at least 16 characters.');
  }
  return { email, password, name };
};

type BootstrapClient = Pick<PrismaClient, 'systemState' | 'user'>;

const ensureSetupState = async (client: BootstrapClient) => {
  await client.systemState.upsert({
    where: { key: 'setup_completed' },
    update: {},
    create: { key: 'setup_completed', boolValue: false },
  });
};

const ensureAdminUser = async (client: BootstrapClient) => {
  if (normalizeBoolean(process.env.SKIP_CONSOLE_SEED)) {
    console.info('[console] Skipping console seed because SKIP_CONSOLE_SEED is set.');
    return;
  }

  const { email, password, name } = resolveAdminCredentials();
  const userCount = await client.user.count();
  if (userCount > 0) {
    const existing = await client.user.findUnique({ where: { email } });
    if (existing?.role === Role.ADMIN) return;
    throw new Error('[console] Users already exist but the configured bootstrap admin is absent; refusing to add or modify credentials.');
  }

  const passwordHash = await bcrypt.hash(password, 12);

  await client.user.create({
    data: { email, password: passwordHash, role: Role.ADMIN, name },
  });

  console.info(`[console] Created initial admin user ${email}`);
};

export async function bootstrapConsole(client: BootstrapClient = prisma) {
  if (!process.env.DATABASE_URL) {
    throw new Error('[console] DATABASE_URL must be set before bootstrapping.');
  }
  if (normalizeBoolean(process.env.CONSOLE_BOOTSTRAP_CHECK)) {
    const { email } = resolveAdminCredentials();
    const [state, admin] = await Promise.all([
      client.systemState.findUnique({ where: { key: 'setup_completed' } }),
      client.user.findUnique({ where: { email } }),
    ]);
    if (!state || admin?.role !== Role.ADMIN) {
      throw new Error('[console] Bootstrap state or configured admin is missing.');
    }
    return;
  }
  await ensureSetupState(client);
  await ensureAdminUser(client);
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
