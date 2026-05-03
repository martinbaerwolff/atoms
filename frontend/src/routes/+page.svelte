<script lang="ts">
  import { listAtoms, createAtom, deleteAtom } from "$lib/api/client";
  import type { Atom, CreateAtomInput } from "$lib/api/client";
  import QuickCapture from "$lib/components/QuickCapture.svelte";
  import AtomList from "$lib/components/AtomList.svelte";

  let atoms = $state<Atom[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let toast = $state<string | null>(null);

  function showToast(msg: string) {
    toast = msg;
    setTimeout(() => (toast = null), 3000);
  }

  $effect(() => {
    listAtoms()
      .then((data) => {
        atoms = data;
      })
      .catch(() => {
        error = "Atoms konnten nicht geladen werden.";
      })
      .finally(() => {
        loading = false;
      });
  });

  async function handleCreate(input: CreateAtomInput) {
    const optimistic: Atom = {
      id: crypto.randomUUID(),
      slug: "",
      content: input.content,
      content_json: null,
      type: input.type ?? "note",
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
    atoms = [optimistic, ...atoms];
    try {
      const created = await createAtom(input);
      atoms = atoms.map((a) => (a.id === optimistic.id ? created : a));
    } catch {
      atoms = atoms.filter((a) => a.id !== optimistic.id);
      showToast("Atom konnte nicht gespeichert werden.");
    }
  }

  async function handleDelete(id: string) {
    const prev = atoms;
    atoms = atoms.filter((a) => a.id !== id);
    try {
      await deleteAtom(id);
    } catch {
      atoms = prev;
      showToast("Atom konnte nicht gelöscht werden.");
    }
  }
</script>

<div class="mx-auto flex max-w-3xl flex-col gap-6 px-8 py-10">
  <header>
    <h1 class="text-2xl font-semibold tracking-tight">Atoms</h1>
  </header>

  <QuickCapture onCreate={handleCreate} />

  {#if loading}
    <p class="font-mono text-sm text-[var(--color-text-muted)]">Lade…</p>
  {:else if error}
    <p class="text-sm text-red-500">{error}</p>
  {:else if atoms.length === 0}
    <p class="font-mono text-sm text-[var(--color-text-muted)]">Noch keine Atoms. Los geht's!</p>
  {:else}
    <AtomList {atoms} onDelete={handleDelete} />
  {/if}
</div>

{#if toast}
  <div
    role="alert"
    aria-live="assertive"
    class="fixed bottom-4 right-4 rounded bg-red-600 px-4 py-2 text-sm text-white shadow"
  >
    {toast}
  </div>
{/if}
