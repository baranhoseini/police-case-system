import "@testing-library/jest-dom";
import { vi } from "vitest";

// ✅ Mock the axios instance used by your services
vi.mock("./services/apiClient", async () => {
  return {
    apiClient: {
      get: vi.fn(async () => ({ data: [] })),
      post: vi.fn(async () => ({ data: {} })),
      put: vi.fn(async () => ({ data: {} })),
      patch: vi.fn(async () => ({ data: {} })),
      delete: vi.fn(async () => ({ data: {} })),
    },
  };
});