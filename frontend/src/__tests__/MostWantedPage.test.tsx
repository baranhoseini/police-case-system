import { describe, it, expect } from "vitest";
import React from "react";
import MostWantedPage from "../pages/MostWantedPage";
import { renderWithProviders } from "../testUtils";

describe("MostWantedPage", () => {
  it("renders without crashing", () => {
    const { container } = renderWithProviders(<MostWantedPage />);
    expect(container).toBeTruthy();
  });
});