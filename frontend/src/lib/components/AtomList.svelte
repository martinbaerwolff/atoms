<script lang="ts">
  import type { Atom } from "$lib/api/client";
  import AtomCard from "./AtomCard.svelte";

  let { atoms, onDelete }: { atoms: Atom[]; onDelete: (id: string) => void } = $props();
</script>

<ul class="flex flex-col gap-3">
  {#each atoms as atom (atom.id)}
    <li>
      <AtomCard {atom} {onDelete} />
    </li>
  {/each}
</ul>
