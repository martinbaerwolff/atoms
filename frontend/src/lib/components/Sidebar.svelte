<script lang="ts">
  import { page } from "$app/stores";

  type NavItem = { href: string; label: string; symbol: string };

  const items: NavItem[] = [
    { href: "/", label: "Atoms", symbol: "·" },
    { href: "/people", label: "Personen", symbol: "◯" },
    { href: "/meetings", label: "Meetings", symbol: "▢" },
    { href: "/projects", label: "Projekte", symbol: "△" },
  ];

  function isActive(href: string, pathname: string): boolean {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  }
</script>

<aside
  class="flex h-screen w-14 flex-col items-center gap-1 border-r border-[var(--color-border)] bg-[var(--color-surface-2)] py-4"
>
  {#each items as item (item.href)}
    {@const active = isActive(item.href, $page.url.pathname)}
    <a
      href={item.href}
      title={item.label}
      aria-label={item.label}
      aria-current={active ? "page" : undefined}
      class="flex size-10 items-center justify-center rounded-md text-base transition-colors"
      class:bg-petrol-500={active}
      class:text-white={active}
      class:text-petrol-700={!active}
      class:hover:bg-petrol-50={!active}
    >
      <span aria-hidden="true">{item.symbol}</span>
    </a>
  {/each}
</aside>
