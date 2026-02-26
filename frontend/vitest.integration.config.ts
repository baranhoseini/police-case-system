import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "node",
    include: ["src/__integration__/**/*.test.{ts,tsx}"],
    testTimeout: 60_000,
    hookTimeout: 60_000,
  },
});