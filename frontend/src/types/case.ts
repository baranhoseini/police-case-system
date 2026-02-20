import type { ID, ISODateString } from "./common";

export type CaseStatus = "DRAFT" | "SUBMITTED" | "UNDER_REVIEW" | "ACTIVE" | "CLOSED" | "REJECTED";

export type ComplaintType =
  | "THEFT"
  | "FRAUD"
  | "ASSAULT"
  | "MURDER"
  | "MISSING_PERSON"
  | "CYBER_CRIME"
  | "OTHER";

export type CaseSummary = {
  id: string;
  numericId: number;
  title: string;
  status: CaseStatus;
  complaintType: ComplaintType;
  createdAt: ISODateString;
  updatedAt?: ISODateString;
};

export type CaseDetails = CaseSummary & {
  description: string;
  reporterName?: string;
  reporterContact?: string;
  assignedDetectiveId?: ID;
  evidenceIds: ID[];
  suspectIds: ID[];
};
