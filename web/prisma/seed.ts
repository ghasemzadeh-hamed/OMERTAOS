import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  const admin = await prisma.user.upsert({
    where: { email: 'admin@aion.local' },
    update: {},
    create: {
      email: 'admin@aion.local',
      name: 'Admin',
      role: 'admin',
      passwordHash: 'changeme'
    }
  });

  const project = await prisma.project.upsert({
    where: { id: 1 },
    update: {},
    create: {
      name: 'AION Launch',
      description: 'Default project',
      ownerId: admin.id
    }
  });

  await prisma.task.create({
    data: {
      projectId: project.id,
      title: 'Create onboarding flow',
      description: 'Ensure first-run agent deployment works',
      status: 'todo',
      priority: 'high'
    }
  });
}

main()
  .catch((error) => {
    console.error(error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
