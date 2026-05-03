import { describe, it, expect, vi, beforeEach } from "vitest";
import { listAtoms, createAtom, updateAtom, deleteAtom } from "$lib/api/client";
import type { Atom } from "$lib/api/client";

const mockAtom: Atom = {
  id: "00000000-0000-0000-0000-000000000001",
  slug: "a-2026-05-03-abc123",
  content: "Testinhalt",
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
  created_at: "2026-05-03T10:00:00Z",
  updated_at: "2026-05-03T10:00:00Z",
  deleted_at: null,
};

beforeEach(() => {
  vi.restoreAllMocks();
});

describe("listAtoms", () => {
  it("fetches /api/atoms and returns atoms", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => [mockAtom],
      })
    );
    const result = await listAtoms();
    expect(result).toEqual([mockAtom]);
    expect(fetch).toHaveBeenCalledWith("/api/atoms", undefined);
  });

  it("passes q param as query string", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => [] }));
    await listAtoms({ q: "test" });
    expect(fetch).toHaveBeenCalledWith("/api/atoms?q=test", undefined);
  });

  it("throws on non-ok response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(listAtoms()).rejects.toThrow("HTTP 500");
  });
});

describe("createAtom", () => {
  it("POSTs to /api/atoms with generated slug and returns atom", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockAtom,
      })
    );
    const result = await createAtom({ content: "Testinhalt" });
    expect(result).toEqual(mockAtom);
    const [url, init] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/api/atoms");
    expect(init.method).toBe("POST");
    const body = JSON.parse(init.body as string);
    expect(body.content).toBe("Testinhalt");
    expect(body.slug).toMatch(/^a-\d{4}-\d{2}-\d{2}-[0-9a-f]+$/);
  });

  it("throws on non-ok response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 422 }));
    await expect(createAtom({ content: "x" })).rejects.toThrow("HTTP 422");
  });
});

describe("updateAtom", () => {
  it("PATCHes /api/atoms/:id and returns updated atom", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ ...mockAtom, content: "geändert" }),
      })
    );
    const result = await updateAtom(mockAtom.id, { content: "geändert" });
    expect(result.content).toBe("geändert");
    const [url, init] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string, RequestInit];
    expect(url).toBe(`/api/atoms/${mockAtom.id}`);
    expect(init.method).toBe("PATCH");
  });

  it("throws on non-ok response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 404 }));
    await expect(updateAtom("bad-id", {})).rejects.toThrow("HTTP 404");
  });
});

describe("deleteAtom", () => {
  it("DELETEs /api/atoms/:id", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 204 }));
    await deleteAtom(mockAtom.id);
    const [url, init] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string, RequestInit];
    expect(url).toBe(`/api/atoms/${mockAtom.id}`);
    expect(init.method).toBe("DELETE");
  });

  it("throws on non-ok response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 404 }));
    await expect(deleteAtom("bad-id")).rejects.toThrow("HTTP 404");
  });
});
