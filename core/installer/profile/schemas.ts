import { z } from 'zod';

export const Base = z.object({
  name: z.enum(['user', 'pro', 'enterprise']),
  services: z.object({
    gateway: z.boolean(),
    control: z.boolean(),
    console: z.boolean(),
  }),
  ai: z.object({
    tensorflow: z.boolean(),
    pytorch: z.boolean(),
  }),
  security: z.object({
    hardening: z.boolean(),
  }),
});

export type Profile = z.infer<typeof Base>;
