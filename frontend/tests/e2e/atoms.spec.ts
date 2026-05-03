import { expect, test } from "@playwright/test";

const ATOM_ID = "00000000-0000-0000-0000-000000000001";

function makeAtom(content: string, id = ATOM_ID) {
  return {
    id,
    slug: "a-2026-05-03-test01",
    content,
    content_json: null,
    type: "note",
    status: "open",
    priority: "medium",
    inbox: true,
    reminder: null,
    deadline: null,
    deadline_hard: false,
    project_id: null,
    meeting_id: null,
    assigned_to: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    deleted_at: null,
  };
}

test.describe("Atoms feed", () => {
  test("shows the Atoms heading and QuickCapture form", async ({ page }) => {
    await page.route("/api/atoms", (route) => route.fulfill({ json: [] }));
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1, name: "Atoms" })).toBeVisible();
    await expect(page.getByRole("textbox")).toBeVisible();
    await expect(page.getByRole("button", { name: /anlegen/i })).toBeVisible();
  });

  test("creates an atom and shows it in the feed", async ({ page }) => {
    const content = "E2E Test Atom";
    const created = makeAtom(content);
    await page.route("/api/atoms", (route) => {
      if (route.request().method() === "GET") return route.fulfill({ json: [] });
      return route.fulfill({ status: 201, json: created });
    });
    await page.goto("/");
    await page.getByRole("textbox").fill(content);
    await page.getByRole("button", { name: /anlegen/i }).click();
    await expect(page.getByText(content)).toBeVisible();
  });

  test("created atom persists after reload", async ({ page }) => {
    const content = "Persist Test";
    const created = makeAtom(content);
    let atoms: object[] = [];
    await page.route("/api/atoms", (route) => {
      if (route.request().method() === "GET") return route.fulfill({ json: atoms });
      atoms = [created];
      return route.fulfill({ status: 201, json: created });
    });
    await page.goto("/");
    await page.getByRole("textbox").fill(content);
    await page.getByRole("button", { name: /anlegen/i }).click();
    await expect(page.getByText(content)).toBeVisible();
    await page.reload();
    await expect(page.getByText(content)).toBeVisible();
  });

  test("deletes an atom and it disappears from the feed", async ({ page }) => {
    const content = "Delete Test";
    const atom = makeAtom(content);
    await page.route("/api/atoms", (route) => {
      if (route.request().method() === "GET") return route.fulfill({ json: [atom] });
      return route.fulfill({ status: 201, json: atom });
    });
    await page.route(`/api/atoms/${ATOM_ID}`, (route) => {
      if (route.request().method() === "DELETE") return route.fulfill({ status: 204, body: "" });
      return route.continue();
    });
    await page.goto("/");
    const card = page.locator("article").filter({ hasText: content });
    await expect(card).toBeVisible();
    await card.hover();
    await card.getByRole("button", { name: /löschen/i }).click();
    await expect(card).not.toBeVisible();
  });
});
