// frontend/src/features/auth/AuthContextBase.ts
import { createContext } from "react";
import type { User, RoleKey } from "../../types/user";

export type AuthState = {
  token: string | null;

  // Backend-driven user info (source of truth)
  user: User | null;
  roles: RoleKey[];
  primaryRole: RoleKey | null;

  isAuthenticated: boolean;

  // Updated signature: login returns token + user
  signIn: (token: string, user: User) => void;
  signOut: () => void;

  // Helper to update after calling /auth/me (optional but useful)
  setUser: (user: User | null) => void;
};

export const AuthContext = createContext<AuthState | null>(null);