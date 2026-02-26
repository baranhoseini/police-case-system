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
  phone: string;
  nationalId: string;
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


export async function register(payload: {
  username: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  nationalId: string;
  password: string;
}) {
  const body = {
    username: payload.username.trim(),
    first_name: payload.firstName.trim(),
    last_name: payload.lastName.trim(),
    email: payload.email.trim(),
    phone: payload.phone.trim(),
    national_id: payload.nationalId.trim(),
    password: payload.password,
  };

  const { data } = await apiClient.post("/auth/register/", body);
  return data;
}