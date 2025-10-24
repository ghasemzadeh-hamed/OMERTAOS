import { test, expect } from '@playwright/test';

test('gateway health endpoint', async ({ request }) => {
  const response = await request.get('/healthz');
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.status).toBe('ok');
});
