<script lang="ts">
  import type { AtomType } from '$lib/api/types'

  let { type }: { type: AtomType } = $props()

  const cfg: Record<AtomType, { symbol: string; color: string; label: string }> = {
    note:     { symbol: '□',  color: '#6B7280', label: 'Notiz' },
    thought:  { symbol: '◎',  color: '#8B5CF6', label: 'Gedanke' },
    task:     { symbol: '☐',  color: '#10B981', label: 'Aufgabe' },
    decision: { symbol: '◆',  color: '#F59E0B', label: 'Entscheidung' },
  }
</script>

<span class="icon" style="color: {cfg[type].color}" title={cfg[type].label}>
  {cfg[type].symbol}
</span>

<style>
  .icon {
    font-size: 0.85rem;
    width: 1.2rem;
    display: inline-block;
    text-align: center;
    flex-shrink: 0;
  }
</style>
