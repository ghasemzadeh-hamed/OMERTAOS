import bcrypt from 'bcrypt';
import { prisma } from '@/lib/prisma';

async function main() {
  const email = 'admin@localhost';
  const password = await bcrypt.hash('admin', 10);

  await prisma.user.upsert({
    where: { email },
    update: {},
    create: {
      email,
      password,
      role: 'ADMIN',
      name: 'Admin',
    },
  });

  console.log('Seeded admin account - username/email: admin@localhost (alias: admin), password: admin');
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
