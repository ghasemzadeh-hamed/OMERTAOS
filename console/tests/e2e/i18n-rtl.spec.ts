import { test, expect } from '@playwright/test';

test('toggles RTL layout', async ({ page }) => {
  await page.goto('/dashboard');
  await page.click('button:has-text("EN")');
  await page.click('button:has-text("FA")');
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
});
