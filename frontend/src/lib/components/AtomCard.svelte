<script lang="ts">
  import type { Atom } from "$lib/api/client";

  let { atom, onDelete }: { atom: Atom; onDelete: (id: string) => void } = $props();

  const typeLabels: Record<string, string> = {
    note: "Notiz",
    task: "Aufgabe",
    event: "Event",
    reminder: "Wecker",
    reference: "Referenz",
  };

  const typeBadgeColors: Record<string, string> = {
    note: "bg-blue-100 text-blue-800",
    task: "bg-amber-100 text-amber-800",
    event: "bg-green-100 text-green-800",
    reminder: "bg-purple-100 text-purple-800",
    reference: "bg-gray-100 text-gray-700",
  };

  function relativeTime(iso: string): string {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60_000);
    if (mins < 1) return "gerade eben";
    if (mins < 60) return `vor ${mins} Min.`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `vor ${hours} Std.`;
    const days = Math.floor(hours / 24);
    return `vor ${days} Tag${days > 1 ? "en" : ""}`;
  }
</script>

<article
  class="group relative rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-2)] p-4"
>
  <div class="mb-2 flex items-center gap-2">
    <span
      class="rounded px-1.5 py-0.5 text-xs font-medium {typeBadgeColors[atom.type] ??
        'bg-gray-100 text-gray-700'}"
    >
      {typeLabels[atom.type] ?? atom.type}
    </span>
    <time
      class="ml-auto font-mono text-xs text-[var(--color-text-muted)]"
      datetime={atom.created_at}
    >
      {relativeTime(atom.created_at)}
    </time>
  </div>
  <p class="whitespace-pre-wrap text-sm">{atom.content}</p>
  <button
    onclick={() => onDelete(atom.id)}
    aria-label="Löschen"
    class="absolute right-2 top-2 hidden rounded p-1 text-[var(--color-text-muted)] hover:text-red-500 group-hover:block"
  >
    ×
  </button>
</article>
