import { describe, expect, it } from "vitest";

describe("test runtime", () => {
  it("vitest + jsdom is wired", () => {
    const div = document.createElement("div");
    div.textContent = "Atoms";
    expect(div.textContent).toBe("Atoms");
  });
});
