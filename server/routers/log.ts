import { router, protectedProcedure } from '@/server/trpc';

export const activityRouter = router({
  feed: protectedProcedure.query(async ({ ctx }) => {
    return ctx.prisma.activityLog.findMany({
      orderBy: { createdAt: 'desc' },
      take: 20,
      include: { user: true }
    });
  })
});
