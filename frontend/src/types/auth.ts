import type { ISODateString } from "./common";

export type AuthToken = {
  token: string;
  expiresAt?: ISODateString;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type SignupRequest = {
  fullName: string;
  email: string;
  password: string;
};

export type AuthUser = {
  id: string;
  fullName: string;
  email: string;
  role: string; // will become RoleKey later
};
