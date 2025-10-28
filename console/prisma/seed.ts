import bcrypt from 'bcrypt';
import { prisma } from '@/lib/prisma';

async function main() {
  const email = 'admin@aion.local';
  const password = await bcrypt.hash('Admin@123', 10);

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

  console.log('Seeded admin:', email, 'password: Admin@123');
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
