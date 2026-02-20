import { apiClient } from "./apiClient";

export type LoginPayload = {
  identifier: string;
  password: string;
};

export type LoginResponse = {
  access: string;
  refresh: string;
  user: unknown;
};

export type RegisterPayload = {
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  national_id: string;
  password: string;
};

export type RegisterResponse = {
  id?: number;
  username?: string;
  access?: string;
  refresh?: string;
  user?: unknown;
};

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const body = {
    identifier: payload.identifier.trim(),
    password: payload.password,
  };

  const { data } = await apiClient.post<LoginResponse>("/auth/login/", body);
  return data;
}

export async function register(payload: RegisterPayload): Promise<RegisterResponse> {
  const body = {
    username: payload.username.trim(),
    first_name: payload.first_name.trim(),
    last_name: payload.last_name.trim(),
    email: payload.email.trim(),
    phone: payload.phone.trim(),
    national_id: payload.national_id.trim(),
    password: payload.password,
  };

  const { data } = await apiClient.post<RegisterResponse>("/auth/register/", body);
  return data;
}
