import { test, expect } from '@playwright/test'

test('Full user flow — simulate → history → report', async ({ page }) => {
  await page.goto('http://localhost:5173')
  await page.click('text=Log in')
  await page.fill('input[type=email]', 'test@example.com')
  await page.fill('input[type=password]', 'test123')
  await page.click('text=Log in')

  await page.fill('textarea', 'TSLA-L-50% AAPL-S-50% 2020-01-01 2021-01-01')
  await page.click('text=Simulate')

  await expect(page.locator('text=Sharpe Ratio')).toBeVisible({ timeout: 20000 })

  await page.click('text=History')
  await expect(page.locator('text=Simulation History')).toBeVisible()

  await page.click('text=View')
  await expect(page.locator('text=Download XLSX Report')).toBeVisible()
})
