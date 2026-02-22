import { describe, it, expect } from "vitest";
import React from "react";
import DetectiveBoardPage from "../pages/DetectiveBoardPage";
import { renderWithProviders } from "../testUtils";

describe("DetectiveBoardPage", () => {
  it("renders without crashing", () => {
    const { container } = renderWithProviders(<DetectiveBoardPage />);
    expect(container).toBeTruthy();
  });
});