<script lang="ts">
  import { onMount } from 'svelte'
  import type { Atom, FilterBadge } from '$lib/api/types'
  import { getAtoms, updateAtom } from '$lib/api/atoms'
  import AtomRow from '$lib/components/AtomRow.svelte'
  import FilterBadges from '$lib/components/FilterBadges.svelte'

  let atoms = $state<Atom[]>([])
  let selectedAtom = $state<Atom | null>(null)
  let activeFilter = $state<FilterBadge | null>(null)
  let allExpanded = $state(false)
  let loading = $state(true)
  let error = $state<string | null>(null)

  async function load() {
    loading = true
    error = null
    try {
      atoms = await getAtoms(activeFilter ? { filter_badge: activeFilter } : {})
    } catch (e) {
      error = (e as Error).message
    } finally {
      loading = false
    }
  }

  onMount(load)

  $effect(() => {
    void activeFilter
    load()
  })

  async function handleCapturedToggle(atom: Atom) {
    const updated = await updateAtom(atom.id, { captured: !atom.captured })
    atoms = atoms.map(a => a.id === atom.id ? updated : a)
    if (selectedAtom?.id === atom.id) selectedAtom = updated
  }

  function handleSelect(atom: Atom) {
    selectedAtom = selectedAtom?.id === atom.id ? null : atom
  }
</script>

<div class="app">
  <header>
    <div class="brand">
      <span class="logo">⬡</span>
      <span class="app-name">Atoms</span>
    </div>
    <div class="header-actions">
      <button class="btn-ghost" class:active={!allExpanded} onclick={() => (allExpanded = false)}>
        Kompakt
      </button>
      <button class="btn-ghost" class:active={allExpanded} onclick={() => (allExpanded = true)}>
        Detail
      </button>
      <button class="btn-primary">+ Neu</button>
    </div>
  </header>

  <FilterBadges bind:active={activeFilter} />

  <div class="content" class:panel-open={!!selectedAtom}>
    <div class="list-area">
      {#if loading}
        <p class="empty">Lade…</p>
      {:else if error}
        <p class="empty error">{error}</p>
      {:else if atoms.length === 0}
        <p class="empty">Keine Einträge.</p>
      {:else}
        {#each atoms as atom (atom.id)}
          <AtomRow
            {atom}
            selected={selectedAtom?.id === atom.id}
            expanded={allExpanded}
            onselect={handleSelect}
            oncapturedtoggle={handleCapturedToggle}
          />
        {/each}
      {/if}
    </div>

    {#if selectedAtom}
      <div class="panel-placeholder">
        <p style="padding:1rem; color: var(--text-muted)">Panel kommt in Task 13</p>
        <button onclick={() => (selectedAtom = null)}>✕</button>
      </div>
    {/if}
  </div>
</div>

<style>
  .app { display: flex; flex-direction: column; height: 100vh; overflow: hidden; }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1.5rem;
    height: 3.5rem;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .brand { display: flex; align-items: center; gap: 0.5rem; }
  .logo { font-size: 1.3rem; color: var(--accent); }
  .app-name { font-weight: 600; font-size: 1rem; }
  .header-actions { display: flex; gap: 0.5rem; align-items: center; }

  .btn-ghost {
    background: none;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.35rem 0.75rem;
    font-size: 0.8rem;
    color: var(--text-muted);
  }
  .btn-ghost.active { border-color: var(--accent); color: var(--accent); }
  .btn-primary {
    background: var(--accent);
    border: none;
    border-radius: 6px;
    padding: 0.4rem 0.9rem;
    color: white;
    font-size: 0.85rem;
    font-weight: 500;
  }

  .content { display: flex; flex: 1; overflow: hidden; }
  .list-area { flex: 1; overflow-y: auto; }
  .panel-placeholder {
    width: 360px;
    border-left: 1px solid var(--border);
    flex-shrink: 0;
  }
  .content.panel-open .list-area { flex: 1; }

  .empty { padding: 2rem 1.5rem; color: var(--text-muted); font-size: 0.875rem; }
  .error { color: #EF4444; }
</style>
