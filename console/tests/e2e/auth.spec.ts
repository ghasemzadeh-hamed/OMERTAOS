import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('sign in with credentials form', async ({ page }) => {
    await page.goto('/sign-in');
    await page.fill('input[type="email"]', 'user@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button:has-text("Sign in")');
    await expect(page).toHaveURL(/dashboard/);
  });
});
