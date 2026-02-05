import type { ID, ISODateString } from "./common";

export type RoleKey =
  | "CITIZEN"
  | "POLICE_OFFICER"
  | "DETECTIVE"
  | "CAPTAIN"
  | "JUDGE"
  | "CHIEF"
  | "ADMIN";

export type User = {
  id: ID;
  fullName: string;
  email: string;
  role: RoleKey;
  createdAt?: ISODateString;
};
