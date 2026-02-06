import { createContext } from "react";
import type { RoleKey } from "../../types/user";

export type AuthState = {
  token: string | null;
  role: RoleKey | null;
  isAuthenticated: boolean;
  signIn: (token: string, role?: RoleKey) => void;
  signOut: () => void;
  setRole: (role: RoleKey) => void;
};

export const AuthContext = createContext<AuthState | null>(null);
