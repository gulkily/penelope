const { test, expect } = require("@playwright/test");

test("can create a project and update north star", async ({ page }) => {
  const projectName = `E2E Project ${Date.now()}`;
  const objective = `E2E Objective ${Date.now()}`;

  await page.goto("/projects");
  await page.getByLabel("Project name").fill(projectName);
  await page.getByRole("button", { name: "Add project" }).click();
  await expect(page.getByRole("link", { name: projectName })).toBeVisible();

  await page.getByRole("link", { name: projectName }).click();

  const objectiveInput = page.locator("#objective-input");
  await expect(objectiveInput).toBeEnabled();

  const objectiveResponse = page.waitForResponse((response) => {
    return (
      response.url().includes("/objective") &&
      response.request().method() === "PUT" &&
      response.status() === 200
    );
  });
  await objectiveInput.fill(objective);
  await objectiveResponse;

  const progressResponse = page.waitForResponse((response) => {
    return (
      response.url().includes("/progress") &&
      response.request().method() === "PUT" &&
      response.status() === 200
    );
  });
  await page.evaluate(() => {
    const slider = document.getElementById("progress-slider");
    if (!slider) {
      return;
    }
    slider.value = "50";
    slider.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await progressResponse;
  await expect(page.locator("#progress-percent")).toHaveText("50%");

  await page.reload();
  await expect(page.locator("#objective-input")).toHaveValue(objective);
});
