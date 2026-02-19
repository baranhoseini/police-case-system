import { apiClient } from "./apiClient";
import type { CaseReport } from "../types/report";
import type { CaseDetails, CaseStatus, ComplaintType } from "../types/case";
import type { RoleKey } from "../types/user";
import type { Evidence } from "../types/evidence";
import { listEvidence } from "./evidenceService";
import { listMostWanted } from "./mostWantedService";

type BackendCase = {
  id: number;
  title: string;
  description?: string;
  status: "DRAFT" | "SUBMITTED" | "UNDER_REVIEW" | "OPEN" | "CLOSED" | "INVALIDATED";
  created_at: string;
};

type BackendCrimeScene = {
  exists: boolean;
  is_approved: boolean | null;
  report: string | null;
};

type BackendSolveRequest = {
  submitted_at: string | null;
  note: string;
} | null;

type BackendCaptainDecision = {
  decision: "SEND_TO_TRIAL" | "RELEASE";
  decided_at: string | null;
  comment: string;
  chief_approved: boolean | null;
  chief_at: string | null;
  chief_comment: string;
} | null;

type BackendTrial = {
  verdict: "GUILTY" | "INNOCENT";
  judged_at: string | null;
  punishment_title: string;
  punishment_description: string;
} | null;

type BackendDossier = {
  case: BackendCase;
  complaint: string | null;
  crime_scene: BackendCrimeScene;
  solve_request: BackendSolveRequest;
  captain_decision: BackendCaptainDecision;
  trial: BackendTrial;
};

function normalizeCaseIdToNumber(raw: string): number {
  const trimmed = raw.trim();
  const numeric = trimmed.replace(/^C-/i, "");
  const n = Number(numeric);
  if (!Number.isFinite(n)) throw new Error("Invalid case id");
  return n;
}

function mapStatus(s: BackendCase["status"]): CaseStatus {
  if (s === "OPEN") return "ACTIVE";
  if (s === "INVALIDATED") return "REJECTED";
  return s;
}

function mapComplaintType(_d: BackendDossier): ComplaintType {
  return "OTHER";
}

function buildCaseDetails(d: BackendDossier, evidence: Evidence[]): CaseDetails {
  const evidenceIds = evidence.map((e) => e.id);

  return {
    id: `C-${d.case.id}`,
    title: d.case.title,
    status: mapStatus(d.case.status),
    complaintType: mapComplaintType(d),
    createdAt: d.case.created_at,
    updatedAt: undefined,
    description: d.case.description || d.complaint || "",
    reporterName: undefined,
    reporterContact: undefined,
    assignedDetectiveId: undefined,
    evidenceIds,
    suspectIds: [],
  };
}

export async function generateCaseReport(caseId: string): Promise<CaseReport> {
  const caseNum = normalizeCaseIdToNumber(caseId);

  const [{ data: dossier }, evidence, mostWanted] = await Promise.all([
    apiClient.get<BackendDossier>(`/cases/${caseNum}/dossier/`),
    listEvidence({ caseId: `C-${caseNum}` }),
    listMostWanted().catch(() => []),
  ]);

  const caseDetails = buildCaseDetails(dossier, evidence);

  const generatedAt = new Date().toISOString();

  return {
    id: `R-${caseNum}-${Date.now()}`,
    generatedAt,
    generatedBy: {
      id: "me",
      fullName: "Current user",
      role: "DETECTIVE" as RoleKey,
    },
    notes: undefined,
    case: caseDetails,
    evidence,
    involvedUsers: [],
    mostWanted,
  };
}
