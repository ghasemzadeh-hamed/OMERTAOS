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
  prisma?: PrismaClient | null;
};

const prismaEnabledEnv = process.env.AION_ENABLE_PRISMA;
const prismaEnabled =
  prismaEnabledEnv === undefined ||
  prismaEnabledEnv === '1' ||
  prismaEnabledEnv.toLowerCase?.() === 'true';

const createPrismaClient = (): PrismaClient | null => {
  if (!prismaEnabled) {
    return null;
  }

  try {
    return new PrismaClient({
      log: ['warn', 'error'],
    });
  } catch (error) {
    // eslint-disable-next-line no-console
    console.warn('[console] Prisma client unavailable; skipping database client init.', error);
    return null;
  }
};

const globalForPrisma = globalThis as GlobalWithPrisma;
const prismaInstance = globalForPrisma.prisma ?? createPrismaClient();

export const prisma: PrismaClient =
  prismaInstance ??
  (new Proxy(
    {},
    {
      get: (_target, prop: string) => {
        if (prop === '$disconnect') {
          return async () => undefined;
        }
        return () => Promise.reject(new Error('Prisma client is disabled'));
      },
    },
  ) as PrismaClient);

if (process.env.NODE_ENV !== 'production' && prismaInstance) {
  globalForPrisma.prisma = prismaInstance;
}
