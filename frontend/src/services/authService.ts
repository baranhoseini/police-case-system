import { apiClient } from "./apiClient";

export type LoginPayload = {
  email: string; 
  password: string;
};

export type LoginResponse = {
  access: string;
  refresh: string;
  user: unknown;
};

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const body = {
    identifier: payload.email.trim(),
    password: payload.password,
  };

  const { data } = await apiClient.post<LoginResponse>("/auth/login/", body);
  return data;
}
