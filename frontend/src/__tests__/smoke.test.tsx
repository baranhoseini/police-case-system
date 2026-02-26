import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import React from "react";

describe("smoke", () => {
  it("renders", () => {
    const { container } = render(<div>Hello</div>);
    expect(container.textContent).toContain("Hello");
  });
});