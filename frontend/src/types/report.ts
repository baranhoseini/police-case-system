import type { ID, ISODateString } from "./common";
import type { CaseDetails } from "./case";
import type { Evidence } from "./evidence";
import type { User } from "./user";
import type { MostWantedItem } from "./mostWanted";

export type CaseReport = {
  id: ID;
  case: CaseDetails;
  evidence: Evidence[];
  involvedUsers: User[];
  mostWanted?: MostWantedItem[];
  generatedAt: ISODateString;
  generatedBy: Pick<User, "id" | "fullName" | "role">;
  notes?: string;
};
