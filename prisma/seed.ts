import { PrismaClient } from '@prisma/client'
import { hash } from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  const password = await hash('admin123', 10)
  await prisma.user.upsert({
    where: { email: 'admin@aion.local' },
    update: {},
    create: {
      email: 'admin@aion.local',
      password,
      role: 'admin'
    }
  })
}

main()
  .catch((error) => {
    console.error(error)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
