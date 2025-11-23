#!/usr/bin/env node
require('dotenv/config');
const { spawnSync } = require('node:child_process');
const path = require('node:path');

if (process.env.SKIP_PRISMA_GENERATE === 'true') {
  console.log('Skipping Prisma generate because SKIP_PRISMA_GENERATE=true');
  process.exit(0);
}

const env = { ...process.env };
if (!env.DATABASE_URL) {
  env.DATABASE_URL = 'file:./dev.db';
  console.warn(
    'DATABASE_URL not set. Falling back to local SQLite database for prisma generate.'
  );
}

const prismaCli = require.resolve('prisma/build/index.js');
const result = spawnSync(process.execPath, [prismaCli, 'generate'], {
  stdio: 'inherit',
  env,
  cwd: path.resolve(__dirname, '..'),
});

if (result.status !== 0) {
  process.exit(result.status ?? 1);
}
