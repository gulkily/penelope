const { test, expect } = require("@playwright/test");

test("dashboard loads", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle("North Star Dashboard");
});
