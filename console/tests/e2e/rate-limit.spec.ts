import { test, expect } from '@playwright/test';

test('shows rate limit feedback', async ({ page }) => {
  await page.goto('/tasks');
  for (let i = 0; i < 5; i += 1) {
    await page.click('button:has-text("Submit task")');
  }
  await expect(page.locator('text=Rate limit')).toBeVisible();
});
