// Minimal helper to demonstrate typed API interactions via TanStack Query.
import { createTask, listTasks } from './api';

export const apiClient = {
  listTasks,
  createTask,
};
