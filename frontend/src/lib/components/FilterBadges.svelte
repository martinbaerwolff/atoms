<script lang="ts">
  import type { FilterBadge } from '$lib/api/types'

  let { active = $bindable(null) }: { active?: FilterBadge | null } = $props()

  const badges: { id: FilterBadge; label: string }[] = [
    { id: 'inbox',        label: 'Inbox' },
    { id: 'created_today', label: 'Heute erstellt' },
    { id: 'updated_today', label: 'Heute geändert' },
    { id: 'overdue',      label: 'Überfällig' },
  ]

  function toggle(id: FilterBadge) {
    active = active === id ? null : id
  }
</script>

<div class="badges">
  {#each badges as badge}
    <button
      class="badge"
      class:active={active === badge.id}
      onclick={() => toggle(badge.id)}
    >
      {badge.label}
    </button>
  {/each}
</div>

<style>
  .badges {
    display: flex;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border-bottom: 1px solid var(--border);
  }
  .badge {
    padding: 0.3rem 0.75rem;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: transparent;
    color: var(--text-muted);
    font-size: 0.8rem;
    transition: all 0.1s;
  }
  .badge:hover { border-color: var(--accent); color: var(--accent); }
  .badge.active { background: var(--accent); border-color: var(--accent); color: white; }
</style>
