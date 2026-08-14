import { test, expect } from '@playwright/test';

test('creates task and shows live update placeholder', async ({ page }) => {
  await page.goto('/tasks');
  await page.fill('textarea', '{"text":"demo"}');
  await page.click('button:has-text("Submit task")');
  await expect(page.locator('text=Task submitted')).toBeVisible();
});
