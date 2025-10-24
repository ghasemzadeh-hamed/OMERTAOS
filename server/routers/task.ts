import { z } from 'zod';
import { protectedProcedure, router } from '@/server/trpc';

export const taskRouter = router({
  list: protectedProcedure
    .input(
      z.object({
        projectId: z.string().optional(),
        query: z.string().optional()
      })
    )
    .query(async ({ ctx, input }) => {
      return ctx.prisma.task.findMany({
        where: {
          projectId: input.projectId,
          title: input.query ? { contains: input.query, mode: 'insensitive' } : undefined
        },
        include: {
          assignee: true
        }
      });
    }),
  create: protectedProcedure
    .input(
      z.object({
        projectId: z.string(),
        title: z.string().min(2),
        description: z.string().optional(),
        assigneeId: z.string().optional()
      })
    )
    .mutation(async ({ ctx, input }) => {
      return ctx.prisma.task.create({
        data: {
          title: input.title,
          description: input.description,
          projectId: input.projectId,
          assigneeId: input.assigneeId
        }
      });
    })
});
