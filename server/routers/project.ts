import { z } from 'zod';
import { protectedProcedure, router } from '@/server/trpc';

export const projectRouter = router({
  list: protectedProcedure.query(async ({ ctx }) => {
    return ctx.prisma.project.findMany({
      include: {
        tasks: true
      }
    });
  }),
  create: protectedProcedure
    .input(
      z.object({
        name: z.string().min(2),
        description: z.string().optional()
      })
    )
    .mutation(async ({ ctx, input }) => {
      return ctx.prisma.project.create({
        data: {
          name: input.name,
          description: input.description
        }
      });
    })
});
