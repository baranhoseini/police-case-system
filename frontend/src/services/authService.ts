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

export type RegisterPayload = {
  fullName: string;
  email: string;
  password: string;
};

export type RegisterResponse = {
  access?: string;
  refresh?: string;
  user?: unknown;
};

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const body = {
    identifier: payload.email.trim(),
    password: payload.password,
  };

  const { data } = await apiClient.post<LoginResponse>("/auth/login/", body);
  return data;
}

export async function register(payload: RegisterPayload): Promise<RegisterResponse> {
  const body = {
    full_name: payload.fullName.trim(),
    email: payload.email.trim(),
    password: payload.password,
  };

  const { data } = await apiClient.post<RegisterResponse>("/auth/register/", body);
  return data;
}
