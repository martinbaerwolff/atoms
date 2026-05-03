import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";
import AtomCard from "$lib/components/AtomCard.svelte";
import type { Atom } from "$lib/api/client";

const mockAtom: Atom = {
  id: "00000000-0000-0000-0000-000000000001",
  slug: "a-2026-05-03-abc123",
  content: "Testinhalt für den Atom",
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

describe("AtomCard", () => {
  it("renders the atom content", () => {
    render(AtomCard, { props: { atom: mockAtom, onDelete: vi.fn() } });
    expect(screen.getByText("Testinhalt für den Atom")).toBeTruthy();
  });

  it("renders the type badge", () => {
    render(AtomCard, { props: { atom: mockAtom, onDelete: vi.fn() } });
    expect(screen.getByText(/notiz/i)).toBeTruthy();
  });

  it("renders a task type badge for task atoms", () => {
    const taskAtom: Atom = { ...mockAtom, type: "task" };
    render(AtomCard, { props: { atom: taskAtom, onDelete: vi.fn() } });
    expect(screen.getByText(/aufgabe/i)).toBeTruthy();
  });

  it("calls onDelete with atom id when delete button is clicked", async () => {
    const onDelete = vi.fn();
    render(AtomCard, { props: { atom: mockAtom, onDelete } });
    const deleteBtn = screen.getByRole("button", { name: /löschen/i });
    await fireEvent.click(deleteBtn);
    expect(onDelete).toHaveBeenCalledOnce();
    expect(onDelete).toHaveBeenCalledWith(mockAtom.id);
  });

  it("renders relative time for created_at", () => {
    render(AtomCard, { props: { atom: mockAtom, onDelete: vi.fn() } });
    // Just check a time element exists — exact text depends on locale/now
    expect(document.querySelector("time")).toBeTruthy();
  });
});
