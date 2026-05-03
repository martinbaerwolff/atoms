import { expect, test } from "@playwright/test";

test.describe("Atoms feed", () => {
  test("shows the Atoms heading and QuickCapture form", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1, name: "Atoms" })).toBeVisible();
    await expect(page.getByRole("textbox")).toBeVisible();
    await expect(page.getByRole("button", { name: /anlegen/i })).toBeVisible();
  });

  test("creates an atom and shows it in the feed", async ({ page }) => {
    await page.goto("/");
    const content = `E2E Test Atom ${Date.now()}`;
    await page.getByRole("textbox").fill(content);
    await page.getByRole("button", { name: /anlegen/i }).click();
    await expect(page.getByText(content)).toBeVisible();
  });

  test("created atom persists after reload", async ({ page }) => {
    await page.goto("/");
    const content = `Persist Test ${Date.now()}`;
    await page.getByRole("textbox").fill(content);
    await page.getByRole("button", { name: /anlegen/i }).click();
    await expect(page.getByText(content)).toBeVisible();
    await page.reload();
    await expect(page.getByText(content)).toBeVisible();
  });

  test("deletes an atom and it disappears from the feed", async ({ page }) => {
    await page.goto("/");
    const content = `Delete Test ${Date.now()}`;
    await page.getByRole("textbox").fill(content);
    await page.getByRole("button", { name: /anlegen/i }).click();
    const card = page.locator("article").filter({ hasText: content });
    await expect(card).toBeVisible();
    await card.hover();
    await card.getByRole("button", { name: /löschen/i }).click();
    await expect(card).not.toBeVisible();
  });
});
