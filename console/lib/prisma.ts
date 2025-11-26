const DEFAULT_SQLITE_URL = 'file:./dev.db';

if (!process.env.DATABASE_URL) {
  process.env.DATABASE_URL = DEFAULT_SQLITE_URL;
  // eslint-disable-next-line no-console
  console.warn(
    `[console] DATABASE_URL not set; defaulting to local SQLite database at ${DEFAULT_SQLITE_URL}. ` +
      'Set DATABASE_URL to a Postgres DSN for production.',
  );
}

type PrismaClientLike = Record<string, any> & {
  $disconnect?: () => Promise<void>;
};

type GlobalWithPrisma = typeof globalThis & {
  prisma?: PrismaClientLike | null;
};

const prismaEnabled = process.env.AION_ENABLE_PRISMA === '1' || process.env.AION_ENABLE_PRISMA === 'true';

let PrismaClientConstructor: { new (...args: any[]): PrismaClientLike } | null = null;

if (prismaEnabled) {
  try {
    const prismaModule = require('@prisma/client');
    PrismaClientConstructor = prismaModule.PrismaClient ?? null;
    if (!PrismaClientConstructor) {
      // eslint-disable-next-line no-console
      console.warn('[console] @prisma/client is installed without generated client; continuing without Prisma.');
    }
  } catch (error) {
    // eslint-disable-next-line no-console
    console.warn('[console] Prisma client unavailable; skipping database client init.', error);
  }
}

const createPrismaClient = (): PrismaClientLike | null => {
  if (!PrismaClientConstructor) {
    return null;
  }
  return new PrismaClientConstructor({
    log: ['warn', 'error'],
  });
};

const createNoopClient = (): PrismaClientLike => {
  const handler: ProxyHandler<Record<string, unknown>> = {
    get: (_target, prop: string) => {
      if (prop === '$disconnect') {
        return async () => undefined;
      }
      const callable = () => Promise.resolve(null);
      return new Proxy(callable, {
        apply: () => Promise.resolve(null),
      });
    },
  };

  return new Proxy({}, handler) as PrismaClientLike;
};

const globalForPrisma = globalThis as GlobalWithPrisma;

const prismaInstance = globalForPrisma.prisma ?? createPrismaClient() ?? createNoopClient();

export const prisma: PrismaClientLike = prismaInstance;

if (process.env.NODE_ENV !== 'production' && prismaInstance) {
  globalForPrisma.prisma = prismaInstance;
}
