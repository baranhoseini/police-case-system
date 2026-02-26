import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5174,
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/setupTests.ts",
    globals: true,

    // ✅ Only run YOUR tests
    include: ["src/__tests__/**/*.test.{ts,tsx}", "src/__integration__/**/*.test.{ts,tsx}"],

    // ✅ Never run dependency or Playwright tests with Vitest
    exclude: ["**/node_modules/**", "tests/**"],
  },
});