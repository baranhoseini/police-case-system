import { defineConfig } from "@playwright/test";

export default defineConfig({
  use: {
    baseURL: "http://localhost:5174",
  },
  webServer: [
    {
      command: "cd .. && docker compose up --build",
      url: "http://localhost:5174",
      timeout: 120000,
      reuseExistingServer: true,
    },
  ],
});