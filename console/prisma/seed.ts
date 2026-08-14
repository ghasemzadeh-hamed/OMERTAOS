import bcrypt from 'bcrypt';

type PrismaClientLike = {
  $connect: () => Promise<void>;
  $disconnect: () => Promise<void>;
  user?: {
    upsert?: (args: Record<string, any>) => Promise<any>;
  };
};

const prismaModule = require('@prisma/client') as {
  PrismaClient?: new (options?: { log?: string[] }) => PrismaClientLike;
};

if (!prismaModule.PrismaClient) {
  throw new Error('Prisma client is missing PrismaClient export. Run prisma generate.');
}

const prisma = new prismaModule.PrismaClient({ log: ['warn', 'error'] });

async function main() {
  const skipSeed = (process.env.SKIP_CONSOLE_SEED || '').toLowerCase();
  if (skipSeed === '1' || skipSeed === 'true' || skipSeed === 'yes') {
    console.log('[console] SKIP_CONSOLE_SEED enabled; skipping seed.');
    return;
  }

  const email = process.env.CONSOLE_ADMIN_EMAIL || 'admin@local';
  const password = process.env.CONSOLE_ADMIN_PASSWORD || 'admin123';
  const name = process.env.CONSOLE_ADMIN_NAME || 'Console Admin';

  const passwordHash = await bcrypt.hash(password, 12);

  await prisma.$connect();

  if (typeof prisma.user?.upsert !== 'function') {
    throw new Error('Prisma client is missing the User model. Run prisma generate.');
  }

  await prisma.user.upsert({
    where: { email },
    update: {
      password: passwordHash,
      role: 'ADMIN',
      name,
    },
    create: {
      email,
      password: passwordHash,
      role: 'ADMIN',
      name,
    },
  });

  console.log(`[console] Seeded admin user ${email}`);
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (error) => {
    console.error('[console] Seed failed', error);
    await prisma.$disconnect();
    process.exit(1);
  });
