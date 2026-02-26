import { test, expect } from "@playwright/test";

test("home loads", async ({ page }) => {
  await page.goto("/");
  await expect(page).toBeVisible();
});

test("cases page calls backend (should not be 404)", async ({ page }) => {
  const responses: number[] = [];
  page.on("response", (r) => {
    if (r.url().includes("/api/cases/")) responses.push(r.status());
  });

  await page.goto("/cases");
  // give it a moment to fetch
  await page.waitForTimeout(1000);

  // If backend is reachable, you should see at least one response status
  expect(responses.length).toBeGreaterThan(0);
  // Usually 200 or 401/403 (auth). 404 means mismatch route.
  expect(responses[0]).not.toBe(404);
});