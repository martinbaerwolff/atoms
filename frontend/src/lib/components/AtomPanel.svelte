<script lang="ts">
  import type { Atom, AtomUpdate, AtomType, AtomStatus, AtomPriority, AtomComplexity, Person, Project } from '$lib/api/types'
  import PersonAvatar from './PersonAvatar.svelte'
  import ProjectBadge from './ProjectBadge.svelte'
  import TypeIcon from './TypeIcon.svelte'

  let {
    atom,
    allPersons,
    allProjects,
    onsave,
    ondelete,
    onclose,
  }: {
    atom: Atom
    allPersons: Person[]
    allProjects: Project[]
    onsave: (id: string, data: AtomUpdate) => Promise<void>
    ondelete: (id: string) => Promise<void>
    onclose: () => void
  } = $props()

  let title = $state(atom.title)
  let content = $state(atom.content)
  let type = $state<AtomType>(atom.type)
  let captured = $state(atom.captured)
  let status = $state<AtomStatus | null>(atom.status)
  let priority = $state<AtomPriority | null>(atom.priority)
  let complexity = $state<AtomComplexity | null>(atom.complexity)
  let deadline_date = $state(atom.deadline_date ? atom.deadline_date.slice(0, 16) : '')
  let alarm_date = $state(atom.alarm_date ? atom.alarm_date.slice(0, 16) : '')
  let source_url = $state(atom.source_url ?? '')
  let responsible_ids = $state(atom.responsible.map(p => p.id))
  let participant_ids = $state(atom.participants.map(p => p.id))
  let project_ids = $state(atom.projects.map(p => p.id))

  let saving = $state(false)
  let confirmDelete = $state(false)

  $effect(() => {
    title = atom.title
    content = atom.content
    type = atom.type
    captured = atom.captured
    status = atom.status
    priority = atom.priority
    complexity = atom.complexity
    deadline_date = atom.deadline_date ? atom.deadline_date.slice(0, 16) : ''
    alarm_date = atom.alarm_date ? atom.alarm_date.slice(0, 16) : ''
    source_url = atom.source_url ?? ''
    responsible_ids = atom.responsible.map(p => p.id)
    participant_ids = atom.participants.map(p => p.id)
    project_ids = atom.projects.map(p => p.id)
  })

  async function save() {
    saving = true
    await onsave(atom.id, {
      title, content, type, captured, status, priority, complexity,
      deadline_date: deadline_date ? new Date(deadline_date).toISOString() : null,
      alarm_date: alarm_date ? new Date(alarm_date).toISOString() : null,
      source_url: source_url || null,
      responsible_ids,
      participant_ids,
      project_ids,
    })
    saving = false
  }

  async function handleDelete() {
    if (!confirmDelete) { confirmDelete = true; return }
    await ondelete(atom.id)
  }

  function toggleId(ids: string[], id: string): string[] {
    return ids.includes(id) ? ids.filter(x => x !== id) : [...ids, id]
  }

  const TYPE_LABELS: Record<AtomType, string> = {
    note: 'Notiz', thought: 'Gedanke', task: 'Aufgabe', decision: 'Entscheidung'
  }
  const STATUS_LABELS: Record<AtomStatus, string> = {
    open: 'Offen', in_progress: 'Läuft', blocked: 'Blockiert', done: 'Erledigt', cancelled: 'Abgebrochen'
  }
  const PRIORITY_LABELS: Record<AtomPriority, string> = {
    high: 'Hoch', medium: 'Mittel', low: 'Niedrig'
  }
  const COMPLEXITY_LABELS: Record<AtomComplexity, string> = {
    deep: 'Tiefe Arbeit', shallow: 'Oberflächlich', routine: 'Routine'
  }
</script>

<aside class="panel">
  <div class="panel-header">
    <TypeIcon {type} />
    <input class="title-input" bind:value={title} placeholder="Titel" />
    <button class="close-btn" onclick={onclose} aria-label="Schließen">✕</button>
  </div>

  <div class="panel-body">
    <textarea class="content-input" bind:value={content} placeholder="Inhalt (Markdown)…" rows="5"></textarea>

    <section>
      <h3>Kompakt-Felder</h3>

      <div class="field">
        <label>Typ</label>
        <select bind:value={type}>
          {#each Object.entries(TYPE_LABELS) as [val, label]}
            <option value={val}>{label}</option>
          {/each}
        </select>
      </div>

      <div class="field">
        <label>Verantwortlich</label>
        <div class="person-list">
          {#each allPersons as person}
            <button
              class="person-chip"
              class:selected={responsible_ids.includes(person.id)}
              onclick={() => responsible_ids = toggleId(responsible_ids, person.id)}
            >
              <PersonAvatar {person} />
              <span>{person.name}</span>
            </button>
          {/each}
          {#if allPersons.length === 0}
            <span class="muted">Keine Personen vorhanden</span>
          {/if}
        </div>
      </div>

      <div class="field">
        <label>Beteiligt</label>
        <div class="person-list">
          {#each allPersons as person}
            <button
              class="person-chip"
              class:selected={participant_ids.includes(person.id)}
              onclick={() => participant_ids = toggleId(participant_ids, person.id)}
            >
              <PersonAvatar {person} />
              <span>{person.name}</span>
            </button>
          {/each}
        </div>
      </div>

      <div class="field">
        <label>Projekte</label>
        <div class="project-list">
          {#each allProjects as project}
            <button
              class="project-chip"
              class:selected={project_ids.includes(project.id)}
              onclick={() => project_ids = toggleId(project_ids, project.id)}
            >
              <ProjectBadge {project} />
            </button>
          {/each}
          {#if allProjects.length === 0}
            <span class="muted">Keine Projekte vorhanden</span>
          {/if}
        </div>
      </div>

      <div class="field captured-field">
        <label>Erfasst</label>
        <button
          class="captured-toggle"
          class:active={captured}
          onclick={() => captured = !captured}
        >
          {captured ? '✓ Erfasst' : '○ Nicht erfasst'}
        </button>
      </div>
    </section>

    {#if type === 'task'}
      <section>
        <h3>Aufgaben-Felder</h3>

        <div class="field">
          <label>Status</label>
          <select bind:value={status}>
            <option value={null}>—</option>
            {#each Object.entries(STATUS_LABELS) as [val, label]}
              <option value={val}>{label}</option>
            {/each}
          </select>
        </div>

        <div class="field">
          <label>Priorität</label>
          <select bind:value={priority}>
            <option value={null}>—</option>
            {#each Object.entries(PRIORITY_LABELS) as [val, label]}
              <option value={val}>{label}</option>
            {/each}
          </select>
        </div>

        <div class="field">
          <label>Komplexität</label>
          <select bind:value={complexity}>
            <option value={null}>—</option>
            {#each Object.entries(COMPLEXITY_LABELS) as [val, label]}
              <option value={val}>{label}</option>
            {/each}
          </select>
        </div>

        <div class="field">
          <label>Fälligkeit</label>
          <input type="datetime-local" bind:value={deadline_date} />
        </div>

        <div class="field">
          <label>Wecker</label>
          <input type="datetime-local" bind:value={alarm_date} />
        </div>
      </section>
    {/if}

    <section>
      <h3>Nur Panel</h3>

      <div class="field">
        <label>Quelle</label>
        <input type="url" bind:value={source_url} placeholder="https://…" />
      </div>

      <div class="field readonly">
        <label>Erstellt</label>
        <span>{new Date(atom.created_at).toLocaleString('de-DE')}</span>
      </div>

      <div class="field readonly">
        <label>Geändert</label>
        <span>{new Date(atom.updated_at).toLocaleString('de-DE')}</span>
      </div>
    </section>
  </div>

  <div class="panel-footer">
    <button
      class="btn-danger"
      onclick={handleDelete}
      class:confirm={confirmDelete}
    >
      {confirmDelete ? 'Wirklich löschen?' : 'Löschen'}
    </button>
    <button class="btn-save" onclick={save} disabled={saving}>
      {saving ? 'Speichere…' : 'Speichern'}
    </button>
  </div>
</aside>

<style>
  .panel {
    width: 360px;
    border-left: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    background: var(--bg);
    overflow: hidden;
  }
  .panel-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .title-input {
    flex: 1;
    border: none;
    border-bottom: 1px solid transparent;
    outline: none;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text);
    background: transparent;
    transition: border-color 0.15s;
    padding-bottom: 1px;
  }
  .title-input:hover { border-bottom-color: var(--border); }
  .title-input:focus { border-bottom-color: var(--accent); }
  .close-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 1rem;
    padding: 0.2rem;
  }
  .panel-body {
    flex: 1;
    overflow-y: auto;
    padding: 0.75rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  .content-input {
    width: 100%;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.5rem;
    font-size: 0.8rem;
    resize: vertical;
    outline: none;
    background: var(--bg-hover);
  }
  section h3 {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 0 0 0.5rem;
  }
  .field {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0.6rem;
  }
  .field label {
    width: 6rem;
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding-top: 0.2rem;
    flex-shrink: 0;
  }
  .field select, .field input[type="url"], .field input[type="datetime-local"] {
    flex: 1;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
    background: var(--bg);
    color: var(--text);
  }
  .field.readonly span { font-size: 0.8rem; color: var(--text-muted); padding-top: 0.2rem; }
  .person-list, .project-list {
    flex: 1;
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
  }
  .person-chip, .project-chip {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.2rem 0.5rem;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: transparent;
    font-size: 0.75rem;
    cursor: pointer;
    opacity: 0.5;
  }
  .person-chip.selected, .project-chip.selected {
    opacity: 1;
    border-color: var(--accent);
  }
  .captured-toggle {
    background: none;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.25rem 0.6rem;
    font-size: 0.8rem;
    cursor: pointer;
    color: var(--text-muted);
  }
  .captured-toggle.active { border-color: var(--accent); color: var(--accent); }
  .muted { font-size: 0.75rem; color: var(--text-muted); }
  .panel-footer {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-top: 1px solid var(--border);
    flex-shrink: 0;
  }
  .btn-save {
    background: var(--accent);
    border: none;
    border-radius: 6px;
    padding: 0.4rem 1rem;
    color: white;
    font-size: 0.85rem;
    font-weight: 500;
  }
  .btn-save:disabled { opacity: 0.6; }
  .btn-danger {
    background: none;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.4rem 0.75rem;
    font-size: 0.8rem;
    color: var(--text-muted);
  }
  .btn-danger.confirm { border-color: #EF4444; color: #EF4444; }
</style>
