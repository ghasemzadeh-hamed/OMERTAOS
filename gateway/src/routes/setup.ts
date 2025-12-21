import type { FastifyInstance } from 'fastify';

const kernelProfiles = [
  { id: 'user', label: 'User', description: 'Default single-tenant developer profile.' },
  {
    id: 'professional',
    label: 'Professional',
    description: 'Multi-user profile with team-ready defaults.',
  },
  {
    id: 'enterprise-vip',
    label: 'Enterprise',
    description: 'Enterprise profile with seal advisor enabled.',
  },
];

export const registerSetupRoutes = (app: FastifyInstance) => {
  app.get('/v1/setup/profile', async () => {
    return {
      profiles: kernelProfiles,
      setupDone: false,
      defaultProfile: 'user',
      updatedAt: new Date().toISOString(),
    };
  });
};
