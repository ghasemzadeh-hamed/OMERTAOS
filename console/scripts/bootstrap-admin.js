/*
 * Ensures a dev/admin user exists using the configured database. This script is
 * idempotent and safe to run during container startup.
 */
const bcrypt = require('bcrypt');
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient({ log: ['warn', 'error'] });

if (!process.env.DATABASE_URL) {
  throw new Error('[console] DATABASE_URL must be set before seeding the admin user.');
}

const normalizeBoolean = (value) => {
  if (!value) return false;
  const normalised = String(value).trim().toLowerCase();
  return ['1', 'true', 'yes', 'on'].includes(normalised);
};

const shouldSeed = () => {
  const skip = normalizeBoolean(process.env.SKIP_CONSOLE_SEED);
  if (skip) {
    console.info('[console] Skipping console seed because SKIP_CONSOLE_SEED is set.');
    return false;
  }
  return true;
};

const resolveAdminCredentials = () => {
  const email =
    process.env.CONSOLE_ADMIN_EMAIL || process.env.DEV_ADMIN_EMAIL || 'admin@local';
  const password =
    process.env.CONSOLE_ADMIN_PASSWORD || process.env.DEV_ADMIN_PASSWORD || 'admin123';
  const name = process.env.CONSOLE_ADMIN_NAME || 'Console Admin';
  return { email, password, name };
};

async function ensureAdminUser() {
  if (!shouldSeed()) {
    return;
  }

  const { email, password, name } = resolveAdminCredentials();
  const passwordHash = await bcrypt.hash(password, 12);

  await prisma.user.upsert({
    where: { email },
    update: { password: passwordHash, role: 'ADMIN', name },
    create: { email, password: passwordHash, role: 'ADMIN', name },
  });

  console.info(`[console] Ensured admin user ${email} in primary datastore.`);
}

module.exports = { ensureAdminUser };

if (require.main === module) {
  ensureAdminUser()
    .then(() => prisma.$disconnect())
    .catch(async (error) => {
      console.error('[console] Failed to seed admin user', error);
      await prisma.$disconnect();
      process.exit(1);
    });
}
