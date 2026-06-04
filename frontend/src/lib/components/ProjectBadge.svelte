<script lang="ts">
  import type { Project } from '$lib/api/types'

  let { project }: { project: Project } = $props()

  const borderColor = project.color ?? '#10B981'
  const textColor = project.color ?? '#10B981'
</script>

<span class="badge" style="border-color: {borderColor}; color: {textColor}">
  {#if project.icon}{project.icon}&nbsp;{/if}{project.name}
</span>

<style>
  .badge {
    display: inline-block;
    padding: 0.1rem 0.4rem;
    border: 1px solid;
    border-radius: 4px;
    font-size: 0.72rem;
    white-space: nowrap;
    line-height: 1.4;
  }
</style>
