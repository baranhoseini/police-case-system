import { describe, it, expect } from "vitest";
import React from "react";
import CasesPage from "../pages/CasesPage";
import { renderWithProviders } from "../testUtils";

describe("CasesPage", () => {
  it("renders without crashing", () => {
    const { container } = renderWithProviders(<CasesPage />);
    expect(container).toBeTruthy();
  });
});