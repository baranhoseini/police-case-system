import type { CaseDetails } from "../types/case";
import type { ID, ISODateString } from "../types/common";

export type CaseTimelineItem = {
  id: ID;
  at: ISODateString;
  title: string;
  description?: string;
};

export type CaseDecision = {
  id: ID;
  at: ISODateString;
  by: string;
  decision: "APPROVED" | "REJECTED" | "NEEDS_MORE_INFO";
  notes?: string;
};

export type CaseDetailsBundle = {
  case: CaseDetails;
  timeline: CaseTimelineItem[];
  decisions: CaseDecision[];
};

const MOCK: Record<string, CaseDetailsBundle> = {
  "C-1001": {
    case: {
      id: "C-1001",
      title: "Stolen vehicle near central station",
      status: "ACTIVE",
      complaintType: "THEFT",
      createdAt: "2026-02-01T09:20:00Z",
      updatedAt: "2026-02-03T12:10:00Z",
      description:
        "A vehicle was reported stolen near the central station. Initial witness statements indicate suspicious activity around 22:15.",
      reporterName: "Alex Johnson",
      reporterContact: "+49 000 000000",
      assignedDetectiveId: "U-22",
      evidenceIds: ["E-3001", "E-3002"],
      suspectIds: ["S-9001"],
    },
    timeline: [
      {
        id: "T-1",
        at: "2026-02-01T09:20:00Z",
        title: "Complaint submitted",
        description: "Citizen submitted the complaint with initial details.",
      },
      {
        id: "T-2",
        at: "2026-02-02T10:10:00Z",
        title: "Evidence registered",
        description: "CCTV snapshot and a witness statement were added.",
      },
      {
        id: "T-3",
        at: "2026-02-03T12:10:00Z",
        title: "Case activated",
        description: "The case status was set to Active by an officer.",
      },
    ],
    decisions: [
      {
        id: "D-1",
        at: "2026-02-03T13:30:00Z",
        by: "Captain Morgan",
        decision: "APPROVED",
        notes: "Proceed with vehicle tracking and interview witnesses.",
      },
    ],
  },
};

export async function getCaseDetails(caseId: string): Promise<CaseDetailsBundle | null> {
  await new Promise((r) => setTimeout(r, 250));
  return MOCK[caseId] ?? null;
}
