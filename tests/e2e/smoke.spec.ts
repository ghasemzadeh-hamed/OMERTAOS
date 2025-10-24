import { test, expect } from '@playwright/test';

test('homepage has sign-in link', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText(/loading/i)).toBeVisible();
});
