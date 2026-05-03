import type { components } from "./types";

export type Atom = components["schemas"]["AtomRead"];
export type AtomType = "note" | "task" | "event" | "reminder" | "reference";
export type AtomStatus = "open" | "in_progress" | "done" | "cancelled" | "waiting";
export type AtomPriority = "low" | "medium" | "high" | "urgent";

export interface CreateAtomInput {
  content: string;
  type?: AtomType;
  status?: AtomStatus;
  priority?: AtomPriority;
  inbox?: boolean;
}

export interface UpdateAtomInput {
  content?: string | null;
  type?: AtomType | null;
  status?: AtomStatus | null;
  priority?: AtomPriority | null;
  inbox?: boolean | null;
}

function generateSlug(): string {
  const date = new Date().toISOString().slice(0, 10);
  const rand = Math.random().toString(16).slice(2, 10);
  return `a-${date}-${rand}`;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init);
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

export async function listAtoms(params?: { q?: string }): Promise<Atom[]> {
  let path = "/api/atoms";
  if (params?.q) {
    path += `?q=${encodeURIComponent(params.q)}`;
  }
  return apiFetch<Atom[]>(path, undefined);
}

export async function createAtom(input: CreateAtomInput): Promise<Atom> {
  const body = {
    slug: generateSlug(),
    content: input.content,
    type: input.type ?? "note",
    status: input.status ?? "open",
    priority: input.priority ?? "medium",
    inbox: input.inbox ?? true,
    deadline_hard: false,
    person_ids: [],
  };
  return apiFetch<Atom>("/api/atoms", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function updateAtom(id: string, input: UpdateAtomInput): Promise<Atom> {
  return apiFetch<Atom>(`/api/atoms/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function deleteAtom(id: string): Promise<void> {
  return apiFetch<void>(`/api/atoms/${id}`, { method: "DELETE" });
}
