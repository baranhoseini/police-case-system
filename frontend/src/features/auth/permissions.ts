import type { RoleKey } from "../../types/user";

export type AppModuleKey =
  | "DASHBOARD"
  | "CASES"
  | "EVIDENCE"
  | "DETECTIVE_BOARD"
  | "MOST_WANTED"
  | "CASE_STATUS"
  | "REPORTS"
  | "ADMIN";

export const ROLE_MODULES: Record<RoleKey, AppModuleKey[]> = {
  CITIZEN: ["DASHBOARD", "CASE_STATUS", "MOST_WANTED"],
  POLICE_OFFICER: ["DASHBOARD", "CASES", "EVIDENCE", "CASE_STATUS", "MOST_WANTED"],
  DETECTIVE: ["DASHBOARD", "CASES", "EVIDENCE", "DETECTIVE_BOARD", "CASE_STATUS", "MOST_WANTED"],
  CAPTAIN: ["DASHBOARD", "CASES", "EVIDENCE", "REPORTS", "CASE_STATUS", "MOST_WANTED"],
  JUDGE: ["DASHBOARD", "REPORTS", "CASE_STATUS", "MOST_WANTED"],
  CHIEF: ["DASHBOARD", "REPORTS", "CASE_STATUS", "MOST_WANTED"],
  ADMIN: ["DASHBOARD", "ADMIN", "CASES", "EVIDENCE", "REPORTS", "CASE_STATUS", "MOST_WANTED"],
};

export function canAccessModule(role: RoleKey, module: AppModuleKey): boolean {
  return ROLE_MODULES[role]?.includes(module) ?? false;
}
