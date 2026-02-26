import { describe, it, expect } from "vitest";
import React from "react";
import AuthPage from "../pages/AuthPage";
import { renderWithProviders } from "../testUtils";

describe("AuthPage", () => {
  it("renders without crashing", () => {
    const { container } = renderWithProviders(<AuthPage />);
    expect(container).toBeTruthy();
  });
});