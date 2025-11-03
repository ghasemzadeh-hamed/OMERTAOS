import { test, expect } from '@playwright/test';

test('gateway health endpoint', async ({ request }) => {
  const endpoints = ['/healthz', '/health'];
  for (const endpoint of endpoints) {
    const response = await request.get(endpoint);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.status).toBe('ok');
    expect(body.service).toBe('gateway');
  }
});
