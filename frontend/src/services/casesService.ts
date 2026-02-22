import { apiClient } from "./apiClient";
import type { CaseStatus, CaseSummary, ComplaintType } from "../types/case";

export type GetCasesParams = {
  q?: string;
  status?: CaseStatus | "ALL";
};

type BackendCase = {
  id: number;
  title: string;
  description?: string;
  status: "DRAFT" | "SUBMITTED" | "UNDER_REVIEW" | "OPEN" | "CLOSED" | "INVALIDATED";
  created_at: string;
  updated_at?: string | null;
};

function mapStatus(s: BackendCase["status"]): CaseStatus {
  if (s === "OPEN") return "ACTIVE";
  if (s === "INVALIDATED") return "REJECTED";
  return s;
}

function mapComplaintType(_c: BackendCase): ComplaintType {
  return "OTHER";
}

function mapCase(c: BackendCase): CaseSummary {
  return {
    id: `C-${c.id}`,
    title: c.title,
    status: mapStatus(c.status),
    complaintType: mapComplaintType(c),
    createdAt: c.created_at,
    updatedAt: c.updated_at ?? undefined,
  };
}

export async function getCases(params: GetCasesParams): Promise<CaseSummary[]> {
  const { data } = await apiClient.get<BackendCase[]>("/cases/");

  const mapped = data.map(mapCase);

  const query = (params.q ?? "").trim().toLowerCase();
  const status = params.status ?? "ALL";

  return mapped.filter((c) => {
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
