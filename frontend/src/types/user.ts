export type RoleKey =
  // Document-canonical role names
  | "Administrator"
  | "Chief"
  | "Captain"
  | "Sergent"
  | "Detective"
  | "Police Officer"
  | "Patrol Officer"
  | "Cadet"
  | "Complainant"
  | "Witness"
  | "Suspect"
  | "Criminal"
  | "Judge"
  | "Corenary"
  | "Base user"
  // Extra / referenced in code
  | "Supervisor"
  // Legacy/internal aliases (backend is alias-aware; keep for safety)
  | "Admin"
  | "Officer"
  | "Patrol"
  | "Sergeant"
  | "Coroner"
  | "Citizen";

export type User = {
  id: string;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  national_id: string;
  roles: RoleKey[];
  primary_role: RoleKey | null;
};
