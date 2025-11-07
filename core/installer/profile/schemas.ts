import { z } from 'zod';

export const Base = z.object({
  name: z.enum(['user', 'pro', 'enterprise']),
  services: z.object({
    gateway: z.boolean(),
    control: z.boolean(),
    console: z.boolean(),
  }),
  features: z.object({
    mlflow: z.object({
      enabled: z.boolean(),
    }),
    jupyter: z.object({
      enabled: z.boolean(),
    }),
    docker: z.object({
      enabled: z.boolean(),
    }),
    k8s: z.object({
      enabled: z.boolean(),
    }),
    ldap: z.object({
      enabled: z.boolean(),
    }),
  }),
  security: z.object({
    hardening: z.object({
      level: z.enum(['none', 'standard', 'cis-lite']),
    }),
  }),
});

export type Profile = z.infer<typeof Base>;
