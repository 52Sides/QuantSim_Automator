import { test, expect } from "@playwright/test";

test("register → login → simulate portfolio", async ({ page }) => {
  await page.goto("/");
  await page.click("text=Sign up");
  await page.fill('input[name="email"]', "user@test.com");
  await page.fill('input[name="password"]', "pass123");
  await page.click("text=Register");
  await expect(page.locator("text=Registration successful")).toBeVisible();

  await page.click("text=Log in");
  await page.fill('input[name="email"]', "user@test.com");
  await page.fill('input[name="password"]', "pass123");
  await page.click("text=Login");
  await expect(page.locator("text=Welcome")).toBeVisible();

  await page.fill("textarea", "AAPL-L-100% 2020-01-01 2020-12-31");
  await page.click("text=Simulate");
  await expect(page.locator("text=CAGR")).toBeVisible({ timeout: 10000 });
});
