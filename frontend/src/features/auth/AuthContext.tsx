// frontend/src/features/auth/AuthContext.tsx
import { useMemo, useState, type PropsWithChildren } from "react";
import type { User, RoleKey } from "../../types/user";
import { clearToken, getToken, setToken } from "./authStorage";
import { AuthContext, type AuthState } from "./AuthContextBase";

const USER_KEY = "pcs_user";

function getStoredUser(): User | null {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? (JSON.parse(raw) as User) : null;
}

function setStoredUser(user: User) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearStoredUser() {
  localStorage.removeItem(USER_KEY);
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [token, setTokenState] = useState<string | null>(() => getToken());
  const [user, setUserState] = useState<User | null>(() => getStoredUser());

  const roles: RoleKey[] = user?.roles ?? [];
  const primaryRole: RoleKey | null = user?.primary_role ?? null;

  const value = useMemo<AuthState>(
    () => ({
      token,
      user,
      roles,
      primaryRole,
      isAuthenticated: Boolean(token),

      // Backend is the source of truth for roles.
      signIn: (newToken: string, newUser: User) => {
        setToken(newToken);
        setTokenState(newToken);

        setStoredUser(newUser);
        setUserState(newUser);
      },

      signOut: () => {
        clearToken();
        clearStoredUser();
        setTokenState(null);
        setUserState(null);
      },

      setUser: (newUser: User | null) => {
        if (newUser) setStoredUser(newUser);
        else clearStoredUser();
        setUserState(newUser);
      },
    }),
    [token, user, roles, primaryRole],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}