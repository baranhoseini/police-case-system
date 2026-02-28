import type { RoleKey } from "../../types/user";

export type AppModuleKey =
  | "DASHBOARD"
  | "CASES"
  | "EVIDENCE"
  | "DETECTIVE_BOARD"
  | "MOST_WANTED"
  | "CASE_STATUS"
  | "REPORTS"
  | "ADMIN"
  | "INTAKE";

/**
 * Role -> module access mapping.
 *
 * NOTE:
 * - Keys include the document-canonical role names.
 * - Legacy/internal aliases are also included to avoid runtime gaps.
 */
export const ROLE_MODULES: Record<RoleKey, AppModuleKey[]> = {
  // Base user (document)
  "Base user": ["DASHBOARD", "INTAKE", "CASE_STATUS", "MOST_WANTED"],
  // Legacy alias
  Citizen: ["DASHBOARD", "INTAKE", "CASE_STATUS", "MOST_WANTED"],

  Complainant: ["DASHBOARD", "INTAKE", "CASE_STATUS", "MOST_WANTED"],
  Witness: ["DASHBOARD", "CASE_STATUS", "MOST_WANTED"],

  // Police roles (document)
  "Police Officer": ["DASHBOARD", "CASES", "EVIDENCE", "INTAKE", "CASE_STATUS", "MOST_WANTED"],
  "Patrol Officer": ["DASHBOARD", "CASES", "EVIDENCE", "INTAKE", "CASE_STATUS", "MOST_WANTED"],
  Detective: ["DASHBOARD", "CASES", "EVIDENCE", "DETECTIVE_BOARD", "INTAKE", "CASE_STATUS", "MOST_WANTED"],
  Sergent: ["DASHBOARD", "CASES", "EVIDENCE", "REPORTS", "INTAKE", "CASE_STATUS", "MOST_WANTED"],
  Captain: ["DASHBOARD", "CASES", "EVIDENCE", "REPORTS", "INTAKE", "CASE_STATUS", "MOST_WANTED"],
  Chief: ["DASHBOARD", "REPORTS", "INTAKE", "CASE_STATUS", "MOST_WANTED"],

  // Judicial / medical (document)
  Judge: ["DASHBOARD", "REPORTS", "CASE_STATUS", "MOST_WANTED"],
  Corenary: ["DASHBOARD"],

  // Admin (document)
  Administrator: ["DASHBOARD", "ADMIN", "CASES", "EVIDENCE", "REPORTS", "INTAKE", "CASE_STATUS", "MOST_WANTED"],

  // Case-actor roles (usually not portal login roles, but safe defaults)
  Suspect: ["DASHBOARD"],
  Criminal: ["DASHBOARD"],

  // Extra
  Supervisor: ["DASHBOARD", "CASES", "EVIDENCE", "REPORTS", "INTAKE", "CASE_STATUS", "MOST_WANTED"],
  // Cadets should be able to access Intake to review complaints.
  Cadet: ["DASHBOARD", "INTAKE", "CASE_STATUS", "MOST_WANTED"],

  // Legacy aliases (match the same access)
  Admin: ["DASHBOARD", "ADMIN", "CASES", "EVIDENCE", "REPORTS", "INTAKE", "CASE_STATUS", "MOST_WANTED"],
  Officer: ["DASHBOARD", "CASES", "EVIDENCE", "INTAKE", "CASE_STATUS", "MOST_WANTED"],
  Patrol: ["DASHBOARD", "CASES", "EVIDENCE", "INTAKE", "CASE_STATUS", "MOST_WANTED"],
  Sergeant: ["DASHBOARD", "CASES", "EVIDENCE", "REPORTS", "INTAKE", "CASE_STATUS", "MOST_WANTED"],
  Coroner: ["DASHBOARD"],
};

export function canAccessModule(role: RoleKey | null | undefined, module: AppModuleKey): boolean {
  const r: RoleKey = role ?? "Base user";
  return ROLE_MODULES[r]?.includes(module) ?? false;
}
