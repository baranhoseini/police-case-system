import { apiClient } from "./apiClient";
import type { User } from "../types/user";

export type LoginPayload = {
  email: string; // actually "identifier" (username/email/phone/national id)
  password: string;
};

export type LoginResponse = {
  access: string;
  refresh: string;
  user: User; // must include roles + primary_role from backend
};

export type RegisterPayload = {
  username: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  nationalId: string;
  password: string;
};

export type RegisterResponse = {
  // your backend register likely returns the created user (or a message).
  // keep it flexible to avoid breaking if backend doesn't return tokens here.
  user?: User;
  detail?: string;
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
    username: payload.username.trim(),
    first_name: payload.firstName.trim(),
    last_name: payload.lastName.trim(),
    email: payload.email.trim(),
    phone: payload.phone.trim(),
    national_id: payload.nationalId.trim(),
    password: payload.password,
  };

  const { data } = await apiClient.post<RegisterResponse>("/auth/register/", body);
  return data;
}