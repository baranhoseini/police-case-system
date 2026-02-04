import { apiClient } from "./apiClient";

export type LoginPayload = {
  email: string;
  password: string;
};

export type LoginResponse = {
  token: string;
};

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  // When backend is ready, replace with:
  // const { data } = await apiClient.post<LoginResponse>("/auth/login", payload);
  // return data;

  // ✅ mock (temporary)
  await new Promise((r) => setTimeout(r, 300));
  return { token: `fake-token:${payload.email}:${Date.now()}` };
}
