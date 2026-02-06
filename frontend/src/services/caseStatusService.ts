import type { CaseStatus, ComplaintType } from "../types/case";
import type { ISODateString } from "../types/common";

export type CaseStatusTimelineItem = {
  at: ISODateString;
  status: CaseStatus;
  title: string;
  description?: string;
};

export type CaseStatusResult = {
  caseId: string;
  title: string;
  complaintType: ComplaintType;
  currentStatus: CaseStatus;
  createdAt: ISODateString;
  updatedAt?: ISODateString;
  timeline: CaseStatusTimelineItem[];
};

const MOCK: Record<string, CaseStatusResult> = {
  "C-1001": {
    caseId: "C-1001",
    title: "Stolen vehicle near central station",
    complaintType: "THEFT",
    currentStatus: "ACTIVE",
    createdAt: "2026-02-01T09:20:00Z",
    updatedAt: "2026-02-03T12:10:00Z",
    timeline: [
      {
        at: "2026-02-01T09:20:00Z",
        status: "SUBMITTED",
        title: "Complaint submitted",
        description: "Your complaint was submitted successfully.",
      },
      {
        at: "2026-02-01T11:00:00Z",
        status: "UNDER_REVIEW",
        title: "Under review",
        description: "A duty officer is reviewing your submission.",
      },
      {
        at: "2026-02-03T12:10:00Z",
        status: "ACTIVE",
        title: "Case activated",
        description: "Your case is now active and assigned for investigation.",
      },
    ],
  },

  "C-1002": {
    caseId: "C-1002",
    title: "Suspicious financial transactions",
    complaintType: "FRAUD",
    currentStatus: "UNDER_REVIEW",
    createdAt: "2026-01-28T15:00:00Z",
    updatedAt: "2026-02-02T08:45:00Z",
    timeline: [
      {
        at: "2026-01-28T15:00:00Z",
        status: "SUBMITTED",
        title: "Complaint submitted",
      },
      {
        at: "2026-02-02T08:45:00Z",
        status: "UNDER_REVIEW",
        title: "Under review",
        description: "We may contact you for additional information.",
      },
    ],
  },
};

export async function trackCaseStatus(caseIdOrCode: string): Promise<CaseStatusResult | null> {
  await new Promise((r) => setTimeout(r, 250));
  const key = caseIdOrCode.trim().toUpperCase();
  return MOCK[key] ?? null;
}
