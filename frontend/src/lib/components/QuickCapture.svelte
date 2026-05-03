<script lang="ts">
  import type { AtomType, CreateAtomInput } from "$lib/api/client";

  let { onCreate }: { onCreate: (input: CreateAtomInput) => void } = $props();

  let content = $state("");
  let type = $state<AtomType>("note");

  const types: { value: AtomType; label: string }[] = [
    { value: "note", label: "Notiz" },
    { value: "task", label: "Aufgabe" },
    { value: "event", label: "Event" },
    { value: "reminder", label: "Wecker" },
    { value: "reference", label: "Referenz" },
  ];

  function submit() {
    const trimmed = content.trim();
    if (!trimmed) return;
    onCreate({ content: trimmed, type });
    content = "";
  }

  function onKeyDown(e: KeyboardEvent) {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      submit();
    }
  }
</script>

<div class="flex flex-col gap-2">
  <textarea
    bind:value={content}
    onkeydown={onKeyDown}
    rows={3}
    placeholder="Gedanke, Aufgabe, Notiz… (Ctrl+Enter zum Anlegen)"
    class="w-full resize-none rounded border border-[var(--color-border)] bg-[var(--color-surface-2)] p-3 font-mono text-sm focus:outline-none focus:ring-1 focus:ring-[var(--color-accent)]"
  ></textarea>
  <div class="flex items-center gap-2">
    <select
      bind:value={type}
      class="rounded border border-[var(--color-border)] bg-[var(--color-surface-2)] px-2 py-1 text-sm"
    >
      {#each types as t}
        <option value={t.value}>{t.label}</option>
      {/each}
    </select>
    <button
      onclick={submit}
      class="ml-auto rounded bg-[var(--color-accent)] px-4 py-1 text-sm font-medium text-white hover:opacity-90"
    >
      Anlegen
    </button>
  </div>
</div>
