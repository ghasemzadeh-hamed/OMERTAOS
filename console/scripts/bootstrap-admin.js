/* Compatibility entrypoint. The reviewed implementation is compiled from bootstrap-admin.ts. */
const { bootstrapConsole, prisma } = require('./dist/bootstrap-admin.js');

module.exports = { bootstrapConsole };

if (require.main === module) {
  bootstrapConsole()
    .then(() => prisma.$disconnect())
    .catch(async (error) => {
      console.error('[console] Failed to bootstrap console', error);
      await prisma.$disconnect();
      process.exit(1);
    });
}
