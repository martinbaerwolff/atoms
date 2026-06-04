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
  <div class="row-main">
    <button
      class="expand-btn"
      onclick={(e) => { e.stopPropagation(); rowExpanded = !rowExpanded }}
      aria-label="Aufklappen"
    >
      {isExpanded ? '∨' : '›'}
    </button>

    <TypeIcon type={atom.type} />

    <span class="title" class:strikethrough={atom.status === 'done'}>
      {atom.title}
    </span>

    <div class="meta">
      {#if atom.type === 'task' && atom.status}
        <span class="status-badge status-{atom.status}">
          {STATUS_LABELS[atom.status] ?? atom.status}
        </span>
      {/if}

      {#if atom.type === 'task' && atom.priority}
        <span class="prio prio-{atom.priority}">
          {PRIORITY_LABELS[atom.priority] ?? atom.priority}
        </span>
      {/if}

      {#if atom.type === 'task' && atom.deadline_date}
        <span class="deadline">
          {new Date(atom.deadline_date).toLocaleDateString('de-DE', { day:'numeric', month:'numeric' })}
        </span>
      {/if}

      <div class="avatars">
        {#each atom.responsible as person}
          <PersonAvatar {person} />
        {/each}
      </div>

      <div class="projects">
        {#each atom.projects as project}
          <ProjectBadge {project} />
        {/each}
      </div>

      <button
        class="captured-btn"
        class:is-captured={atom.captured}
        onclick={(e) => { e.stopPropagation(); oncapturedtoggle(atom) }}
        title={atom.captured ? 'Erfasst' : 'Nicht erfasst'}
        aria-label="Erfasst togglen"
      >
        {atom.captured ? '✓' : '○'}
      </button>
    </div>
  </div>

  {#if isExpanded && atom.content}
    <div class="preview">{atom.content}</div>
  {/if}
</div>

<style>
  .row {
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    transition: background 0.1s;
  }
  .row:hover { background: var(--bg-hover); }
  .row.selected { border-left: 3px solid var(--accent); }
  .row-main {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1rem;
    min-height: 2.5rem;
  }
  .expand-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    padding: 0 0.25rem;
    font-size: 0.75rem;
    line-height: 1;
    flex-shrink: 0;
  }
  .title {
    flex: 1;
    font-size: 0.875rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .strikethrough { text-decoration: line-through; color: var(--text-muted); }
  .meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-shrink: 0;
  }
  .status-badge {
    font-size: 0.72rem;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    background: var(--border);
  }
  .status-done { color: var(--accent); background: var(--accent-light); }
  .prio { font-size: 0.72rem; color: var(--text-muted); }
  .prio-high { color: #EF4444; }
  .deadline { font-size: 0.72rem; color: var(--text-muted); }
  .avatars, .projects { display: flex; gap: 0.2rem; align-items: center; }
  .captured-btn {
    background: none;
    border: none;
    font-size: 0.85rem;
    color: var(--text-muted);
    padding: 0.1rem 0.3rem;
  }
  .captured-btn.is-captured { color: var(--accent); }
  .preview {
    padding: 0.25rem 1rem 0.6rem 3rem;
    font-size: 0.8rem;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
  }
</style>
