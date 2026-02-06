import { useMemo, useState, type PropsWithChildren } from "react";
import type { RoleKey } from "../../types/user";
import { clearToken, getToken, setToken } from "./authStorage";
import { AuthContext, type AuthState } from "./AuthContextBase";

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
