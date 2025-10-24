import { router } from '@/server/trpc';
import { projectRouter } from './project';
import { taskRouter } from './task';
import { activityRouter } from './log';

export const appRouter = router({
  project: projectRouter,
  task: taskRouter,
  activity: activityRouter
});

export type AppRouter = typeof appRouter;
