<script lang="ts">
  import type { Person } from '$lib/api/types'

  let { person }: { person: Person } = $props()

  const COLORS = ['#10B981','#8B5CF6','#F59E0B','#3B82F6','#EF4444','#06B6D4','#EC4899']

  function initials(name: string): string {
    return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
  }

  function bg(name: string): string {
    let h = 0
    for (const c of name) h = (h * 31 + c.charCodeAt(0)) >>> 0
    return COLORS[h % COLORS.length]
  }
</script>

<span class="avatar" style="background: {bg(person.name)}" title={person.name}>
  {#if person.photo_url}
    <img src={person.photo_url} alt={person.name} />
  {:else}
    {initials(person.name)}
  {/if}
</span>

<style>
  .avatar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.75rem;
    height: 1.75rem;
    border-radius: 50%;
    color: white;
    font-size: 0.65rem;
    font-weight: 600;
    overflow: hidden;
    flex-shrink: 0;
  }
  .avatar img { width: 100%; height: 100%; object-fit: cover; }
</style>
