import { createContext, useContext, useMemo, useState, type PropsWithChildren } from "react";
import { clearToken, getToken, setToken } from "./authStorage";
import type { RoleKey } from "../../types/user";

type AuthState = {
  token: string | null;
  role: RoleKey | null;
  isAuthenticated: boolean;
  signIn: (token: string, role?: RoleKey) => void;
  signOut: () => void;
  setRole: (role: RoleKey) => void;
};

const AuthContext = createContext<AuthState | null>(null);

const ROLE_KEY = "pcs_role";

function getStoredRole(): RoleKey | null {
  const r = localStorage.getItem(ROLE_KEY);
  return (r as RoleKey) || null;
}

function setStoredRole(role: RoleKey) {
  localStorage.setItem(ROLE_KEY, role);
}

function clearStoredRole() {
  localStorage.removeItem(ROLE_KEY);
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [token, setTokenState] = useState<string | null>(() => getToken());
  const [role, setRoleState] = useState<RoleKey | null>(() => getStoredRole());

  const value = useMemo<AuthState>(
    () => ({
      token,
      role,
      isAuthenticated: Boolean(token),
      signIn: (newToken: string, newRole?: RoleKey) => {
        setToken(newToken);
        setTokenState(newToken);

        const finalRole: RoleKey = newRole ?? role ?? "DETECTIVE";
        setStoredRole(finalRole);
        setRoleState(finalRole);
      },
      signOut: () => {
        clearToken();
        clearStoredRole();
        setTokenState(null);
        setRoleState(null);
      },
      setRole: (newRole: RoleKey) => {
        setStoredRole(newRole);
        setRoleState(newRole);
      },
    }),
    [token, role],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
