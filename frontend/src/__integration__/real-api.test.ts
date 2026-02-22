import { describe, it, expect, beforeAll } from "vitest";
import axios from "axios";
import { apiBase, waitForBackend } from "./helpers";

const USERNAME = process.env.TEST_USER || "testuser1";
const PASSWORD = process.env.TEST_PASS || "TestPass123!";

async function getToken(): Promise<string> {
  const base = apiBase();

  // Try common auth endpoints and payloads
  const candidates = [
    { path: "/token/", bodies: [{ username: USERNAME, password: PASSWORD }] },
    { path: "/token/obtain/", bodies: [{ username: USERNAME, password: PASSWORD }] },
    {
      path: "/auth/login/",
      bodies: [
        { username: USERNAME, password: PASSWORD },
        { identifier: USERNAME, password: PASSWORD },
      ],
    },
    {
      path: "/accounts/login/",
      bodies: [
        { username: USERNAME, password: PASSWORD },
        { identifier: USERNAME, password: PASSWORD },
      ],
    },
    {
      path: "/login/",
      bodies: [
        { username: USERNAME, password: PASSWORD },
        { identifier: USERNAME, password: PASSWORD },
      ],
    },
  ];

  for (const c of candidates) {
    for (const body of c.bodies) {
      const res = await axios.post(`${base}${c.path}`, body, {
        validateStatus: () => true,
      });
      if (res.status >= 200 && res.status < 300) {
        const token = res.data?.access || res.data?.token;
        if (token) return token;
      }
    }
  }

  // Last resort: find something login/token-like in OpenAPI schema
  const schemaRes = await axios.get(`${base}/schema/`, { validateStatus: () => true });
  if (schemaRes.status === 200) {
    const paths: Record<string, any> = schemaRes.data?.paths || {};
    const postPaths = Object.keys(paths).filter((p) => paths[p]?.post);

    const likely = postPaths.find((p) => {
      const post = paths[p]?.post;
      const s = `${p} ${post?.operationId || ""}`.toLowerCase();
      return s.includes("token") || s.includes("login") || s.includes("auth");
    });

    if (likely) {
      for (const body of [
        { username: USERNAME, password: PASSWORD },
        { identifier: USERNAME, password: PASSWORD },
      ]) {
        const res = await axios.post(`${base}${likely}`, body, { validateStatus: () => true });
        if (res.status >= 200 && res.status < 300) {
          const token = res.data?.access || res.data?.token;
          if (token) return token;
        }
      }
    }
  }

  throw new Error("Could not obtain auth token from backend. Tell me your login endpoint path.");
}

describe("Real backend integration (no mocks)", () => {
  beforeAll(async () => {
    await waitForBackend();
  });

  it("GET /cases/ returns 401 without auth", async () => {
    const res = await axios.get(`${apiBase()}/cases/`, { validateStatus: () => true });
    expect(res.status).toBe(401);
  });

  it("GET /cases/ returns 200 with Bearer token", async () => {
    const token = await getToken();
    const res = await axios.get(`${apiBase()}/cases/`, {
      headers: { Authorization: `Bearer ${token}` },
      validateStatus: () => true,
    });
    expect(res.status).toBe(200);
    expect(res.data).toBeTruthy();
  });

  it("GET /suspects/most-wanted/ returns 200 with Bearer token", async () => {
    const token = await getToken();
    const res = await axios.get(`${apiBase()}/suspects/most-wanted/`, {
      headers: { Authorization: `Bearer ${token}` },
      validateStatus: () => true,
    });
    expect(res.status).toBe(200);
    expect(res.data).toBeTruthy();
  });
});