import { test, expect } from '@playwright/test'

test('renders dashboard hero', async ({ page }) => {
  await page.goto('http://localhost:3000')
  await expect(page.getByText('AION-OS')).toBeVisible()
})
