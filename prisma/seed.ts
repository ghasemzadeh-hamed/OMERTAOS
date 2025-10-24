import { prisma } from '../server/db';
import { hashPassword } from '../server/utils/password';

async function main() {
  const adminPassword = await hashPassword('admin123');
  await prisma.user.upsert({
    where: { email: 'admin@aion.space' },
    update: {},
    create: {
      email: 'admin@aion.space',
      name: 'Commander Ada',
      password: adminPassword,
      role: 'admin'
    }
  });

  const project = await prisma.project.create({
    data: {
      name: 'AION Launchpad',
      description: 'Mission critical operations orchestration.'
    }
  });

  await prisma.task.createMany({
    data: [
      {
        title: 'Configure telemetry',
        description: 'Ensure data stream is resilient and cached.',
        projectId: project.id
      },
      {
        title: 'Draft launch briefing',
        description: 'Collect notes from subsystem leads.',
        projectId: project.id
      }
    ]
  });
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (e) => {
    console.error(e);
    await prisma.$disconnect();
    process.exit(1);
  });
