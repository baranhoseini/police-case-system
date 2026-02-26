import axios from "axios";

export function apiBase(): string {
  const base = process.env.VITE_API_BASE_URL || "http://localhost:8000/api";
  return base.replace(/\/+$/, "");
}

export async function waitForBackend(timeoutMs = 60_000) {
  const start = Date.now();
  const url = `${apiBase()}/schema/`;
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await axios.get(url, { validateStatus: () => true });
      if (res.status === 200) return;
    } catch {}
    await new Promise((r) => setTimeout(r, 1000));
  }
  throw new Error(`Backend not ready at ${url} after ${timeoutMs}ms`);
}