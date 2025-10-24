import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './test/e2e',
  use: {
    baseURL: process.env.GATEWAY_BASE_URL || 'http://localhost:8080',
  },
});
