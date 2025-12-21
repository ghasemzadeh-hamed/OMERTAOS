import { PrismaClient } from '@prisma/client';

import { getDatabaseDiagnostics, requirePostgresUrl } from './databaseInfo';

const isDockerEnv = process.env.AION_DOCKER === '1' || process.env.DOCKER === 'true';
const isProdEnv = process.env.NODE_ENV === 'production';
const enforceDatabaseUrl = isDockerEnv || isProdEnv;

const databaseUrl = process.env.DATABASE_URL;
requirePostgresUrl(databaseUrl, enforceDatabaseUrl);

const databaseDiagnostics = getDatabaseDiagnostics(databaseUrl, enforceDatabaseUrl);
// eslint-disable-next-line no-console
console.info(
  `[console] Database provider: ${databaseDiagnostics.provider}; URL: ${databaseDiagnostics.redactedUrl}`,
);

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
