<script lang="ts">
  import type { Atom } from '$lib/api/types'
  import TypeIcon from './TypeIcon.svelte'
  import PersonAvatar from './PersonAvatar.svelte'
  import ProjectBadge from './ProjectBadge.svelte'

  let {
    atom,
    selected = false,
    expanded = false,
    onselect,
    oncapturedtoggle,
  }: {
    atom: Atom
    selected?: boolean
    expanded?: boolean
    onselect: (atom: Atom) => void
    oncapturedtoggle: (atom: Atom) => void
  } = $props()

  let rowExpanded = $state(false)
  let isExpanded = $derived(expanded || rowExpanded)

  const STATUS_LABELS: Record<string, string> = {
    open: 'Offen', in_progress: 'Läuft', blocked: 'Blockiert',
    done: 'Erledigt', cancelled: 'Abgebrochen',
  }
  const PRIORITY_LABELS: Record<string, string> = {
    high: 'Hoch', medium: 'Mittel', low: 'Niedrig',
  }
</script>

<div
  class="row"
  class:selected
  class:done={atom.status === 'done'}
  role="button"
  tabindex="0"
  onclick={() => onselect(atom)}
  onkeydown={(e) => e.key === 'Enter' && onselect(atom)}
>
  <button
    class="col-expand"
    onclick={(e) => { e.stopPropagation(); rowExpanded = !rowExpanded }}
    aria-label="Aufklappen"
  >
    {isExpanded ? '∨' : '›'}
  </button>

  <div class="col-icon">
    <TypeIcon type={atom.type} />
  </div>

  <span class="col-title" class:strikethrough={atom.status === 'done'}>
    {atom.title}
  </span>

  <div class="col-status">
    {#if atom.type === 'task' && atom.status}
      <span class="status-badge status-{atom.status}">
        {STATUS_LABELS[atom.status] ?? atom.status}
      </span>
    {/if}
  </div>

  <div class="col-prio">
    {#if atom.type === 'task' && atom.priority}
      <span class="prio prio-{atom.priority}">
        {PRIORITY_LABELS[atom.priority] ?? atom.priority}
      </span>
    {/if}
  </div>

  <div class="col-deadline">
    {#if atom.type === 'task' && atom.deadline_date}
      <span class="deadline">
        {new Date(atom.deadline_date).toLocaleDateString('de-DE', { day: 'numeric', month: 'numeric' })}
      </span>
    {/if}
  </div>

  <div class="col-persons">
    {#each atom.responsible as person}
      <PersonAvatar {person} />
    {/each}
  </div>

  <div class="col-projects">
    {#each atom.projects as project}
      <ProjectBadge {project} />
    {/each}
  </div>

  <button
    class="col-captured"
    class:is-captured={atom.captured}
    onclick={(e) => { e.stopPropagation(); oncapturedtoggle(atom) }}
    title={atom.captured ? 'Erfasst' : 'Nicht erfasst'}
    aria-label="Erfasst togglen"
  >
    {atom.captured ? '✓' : '○'}
  </button>

  {#if isExpanded && atom.content}
    <div class="preview">{atom.content}</div>
  {/if}
</div>

<style>
  .row {
    display: grid;
    grid-template-columns: var(--atom-cols);
    align-items: center;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    cursor: pointer;
    transition: box-shadow 0.12s, border-color 0.12s;
    min-height: 2.75rem;
  }
  .row:hover {
    border-color: #D1D5DB;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  }
  .row.selected {
    border-color: var(--accent);
    box-shadow: 0 2px 6px rgba(16, 185, 129, 0.15);
  }
  .row.done { opacity: 0.6; }

  .col-expand {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 0.75rem;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px 0 0 8px;
  }
  .col-icon {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .col-title {
    font-size: 0.875rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding-right: 0.75rem;
  }
  .strikethrough { text-decoration: line-through; color: var(--text-muted); }

  .col-status,
  .col-prio,
  .col-deadline,
  .col-persons,
  .col-projects {
    display: flex;
    align-items: center;
    gap: 0.2rem;
    overflow: hidden;
  }

  .status-badge {
    font-size: 0.7rem;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    background: var(--border);
    white-space: nowrap;
  }
  .status-done { color: var(--accent); background: var(--accent-light); }
  .status-in_progress { color: #3B82F6; background: #DBEAFE; }
  .status-blocked { color: #EF4444; background: #FEE2E2; }

  .prio { font-size: 0.72rem; color: var(--text-muted); }
  .prio-high { color: #EF4444; font-weight: 600; }
  .prio-medium { color: #F59E0B; }

  .deadline { font-size: 0.72rem; color: var(--text-muted); }

  .col-captured {
    background: none;
    border: none;
    font-size: 0.85rem;
    color: var(--text-muted);
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0 8px 8px 0;
  }
  .col-captured.is-captured { color: var(--accent); }

  .preview {
    grid-column: 1 / -1;
    padding: 0.5rem 1rem 0.65rem 3.5rem;
    font-size: 0.8rem;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
    border-top: 1px solid var(--border);
  }
</style>
