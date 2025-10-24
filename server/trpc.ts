import { initTRPC, TRPCError } from '@trpc/server';
import superjson from 'superjson';
import { getServerAuthSession } from '@/server/auth';
import { prisma } from '@/server/db';

const t = initTRPC.context<Awaited<ReturnType<typeof createContext>>>().create({
  transformer: superjson
});

export const router = t.router;
export const procedure = t.procedure;

export async function createContext() {
  const session = await getServerAuthSession();
  return { session, prisma };
}

export const protectedProcedure = procedure.use(({ ctx, next }) => {
  if (!ctx.session) {
    throw new TRPCError({ code: 'UNAUTHORIZED' });
  }
  return next({ ctx });
});
