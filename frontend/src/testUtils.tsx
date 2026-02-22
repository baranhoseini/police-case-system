import React, { PropsWithChildren } from "react";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "./features/auth/AuthContext";

function Wrapper({ children }: PropsWithChildren) {
  return (
    <MemoryRouter>
      <AuthProvider>{children}</AuthProvider>
    </MemoryRouter>
  );
}

export function renderWithProviders(ui: React.ReactElement) {
  return render(ui, { wrapper: Wrapper });
}