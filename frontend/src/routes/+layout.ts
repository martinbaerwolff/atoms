// Static-adapter SPA: pre-render disabled, all rendering happens client-side
// against `index.html` (the SPA fallback configured in svelte.config.js).
export const prerender = false;
export const ssr = false;
export const trailingSlash = "never";
