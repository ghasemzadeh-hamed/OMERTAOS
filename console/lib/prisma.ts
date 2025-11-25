import { PrismaClient } from '@prisma/client';

const DEFAULT_SQLITE_URL = 'file:./dev.db';

if (!process.env.DATABASE_URL) {
  process.env.DATABASE_URL = DEFAULT_SQLITE_URL;
  // eslint-disable-next-line no-console
  console.warn(
    `[console] DATABASE_URL not set; defaulting to local SQLite database at ${DEFAULT_SQLITE_URL}. ` +
      'Set DATABASE_URL to a Postgres DSN for production.',
  );
}

type GlobalWithPrisma = typeof globalThis & {
  prisma?: PrismaClient;
};

const globalForPrisma = globalThis as GlobalWithPrisma;

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: ['warn', 'error'],
  });

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}
