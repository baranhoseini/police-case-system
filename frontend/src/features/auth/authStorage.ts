const ACCESS_TOKEN_KEYS = ["pcs_token", "pcs_access_token"];
const REFRESH_TOKEN_KEYS = ["pcs_refresh_token", "pcs_refresh"];

function getFirst(keys: string[]): string | null {
  for (const k of keys) {
    const v = localStorage.getItem(k);
    if (v) return v;
  }
  return null;
}

export function getToken(): string | null {
  return getFirst(ACCESS_TOKEN_KEYS);
}

export function setToken(token: string) {
  localStorage.setItem("pcs_token", token);
}

export function getRefreshToken(): string | null {
  return getFirst(REFRESH_TOKEN_KEYS);
}

export function setRefreshToken(token: string) {
  localStorage.setItem("pcs_refresh_token", token);
}

export function clearToken() {
  for (const k of ACCESS_TOKEN_KEYS) localStorage.removeItem(k);
  for (const k of REFRESH_TOKEN_KEYS) localStorage.removeItem(k);
}
