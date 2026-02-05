import type { CaseStatus, CaseSummary, ComplaintType } from "../types/case";

const MOCK_CASES: CaseSummary[] = [
  {
    id: "C-1001",
    title: "Stolen vehicle near central station",
    status: "ACTIVE",
    complaintType: "THEFT",
    createdAt: "2026-02-01T09:20:00Z",
    updatedAt: "2026-02-03T12:10:00Z",
  },
  {
    id: "C-1002",
    title: "Suspicious financial transactions",
    status: "UNDER_REVIEW",
    complaintType: "FRAUD",
    createdAt: "2026-01-28T15:00:00Z",
    updatedAt: "2026-02-02T08:45:00Z",
  },
  {
    id: "C-1003",
    title: "Missing person report (adult)",
    status: "SUBMITTED",
    complaintType: "MISSING_PERSON",
    createdAt: "2026-02-04T10:30:00Z",
  },
  {
    id: "C-1004",
    title: "Assault case in downtown",
    status: "CLOSED",
    complaintType: "ASSAULT",
    createdAt: "2026-01-18T17:05:00Z",
    updatedAt: "2026-01-26T11:00:00Z",
  },
];

export type GetCasesParams = {
  q?: string;
  status?: CaseStatus | "ALL";
};

export async function getCases(params: GetCasesParams): Promise<CaseSummary[]> {
  await new Promise((r) => setTimeout(r, 250));

  const query = (params.q ?? "").trim().toLowerCase();
  const status = params.status ?? "ALL";

  return MOCK_CASES.filter((c) => {
    const matchesQuery =
      !query ||
      c.id.toLowerCase().includes(query) ||
      c.title.toLowerCase().includes(query) ||
      c.complaintType.toLowerCase().includes(query);

    const matchesStatus = status === "ALL" ? true : c.status === status;

    return matchesQuery && matchesStatus;
  });
}

export function formatCaseStatus(status: CaseStatus): string {
  const map: Record<CaseStatus, string> = {
    DRAFT: "Draft",
    SUBMITTED: "Submitted",
    UNDER_REVIEW: "Under review",
    ACTIVE: "Active",
    CLOSED: "Closed",
    REJECTED: "Rejected",
  };
  return map[status];
}

export function formatComplaintType(t: ComplaintType): string {
  const map: Record<ComplaintType, string> = {
    THEFT: "Theft",
    FRAUD: "Fraud",
    ASSAULT: "Assault",
    MURDER: "Murder",
    MISSING_PERSON: "Missing person",
    CYBER_CRIME: "Cyber crime",
    OTHER: "Other",
  };
  return map[t];
}
