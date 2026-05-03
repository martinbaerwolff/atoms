import { expect, test } from "@playwright/test";

test("landing page shows the Atoms heading and sidebar", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { level: 1, name: "Atoms" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Personen" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Meetings" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Projekte" })).toBeVisible();
});
