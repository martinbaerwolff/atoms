import { defineConfig } from "vitest/config";
import { svelte } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
  plugins: [svelte({ hot: false })],
  test: {
    environment: "jsdom",
    include: ["tests/unit/**/*.{test,spec}.{ts,js,svelte}"],
    setupFiles: ["./tests/setup.ts"],
    globals: true,
  },
});
