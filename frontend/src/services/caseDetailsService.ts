import { apiClient } from "./apiClient";
import type { CaseDetails, CaseStatus, ComplaintType } from "../types/case";
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

type BackendCase = {
  id: number;
  title: string;
  description?: string;
  status: "DRAFT" | "SUBMITTED" | "UNDER_REVIEW" | "OPEN" | "CLOSED" | "INVALIDATED";
  crime_level?: number;
  created_by: number;
  created_at: string;
};

type BackendCrimeScene = {
  exists: boolean;
  is_approved: boolean | null;
  report: string | null;
};

type BackendSolveRequest = {
  id: number;
  suspect_ids: number[];
  note: string;
  status: string;
  submitted_by: number | null;
  submitted_at: string | null;
  reviewed_by: number | null;
  reviewed_at: string | null;
  review_comment: string | null;
} | null;

type BackendInterrogation = {
  id: number;
  suspect_id: number;
  detective_score: number | null;
  sergent_score: number | null;
  created_at: string;
  updated_at: string;
};

type BackendCaptainDecision = {
  decision: "SEND_TO_TRIAL" | "RELEASE";
  comment: string;
  decided_by: number | null;
  decided_at: string | null;
  chief_approved: boolean | null;
  chief_by: number | null;
  chief_at: string | null;
  chief_comment: string;
} | null;

type BackendTrial = {
  verdict: "GUILTY" | "INNOCENT";
  punishment_title: string;
  punishment_description: string;
  judged_by: number | null;
  judged_at: string | null;
} | null;

type BackendDossier = {
  case: BackendCase;
  complaint: string | null;
  crime_scene: BackendCrimeScene;
  solve_request: BackendSolveRequest;
  interrogations: BackendInterrogation[];
  captain_decision: BackendCaptainDecision;
  trial: BackendTrial;
};

function normalizeCaseId(caseId: string): string {
  return caseId.trim().replace(/^C-/i, "");
}

function mapStatus(s: BackendCase["status"]): CaseStatus {
  if (s === "OPEN") return "ACTIVE";
  if (s === "INVALIDATED") return "REJECTED";
  return s;
}

function mapComplaintType(_d: BackendDossier): ComplaintType {
  return "OTHER";
}

function buildTimeline(d: BackendDossier): CaseTimelineItem[] {
  const items: CaseTimelineItem[] = [];

  items.push({
    id: `T-created`,
    at: d.case.created_at,
    title: "Case created",
  });

  if (typeof d.complaint === "string" && d.complaint.trim()) {
    items.push({
      id: `T-complaint`,
      at: d.case.created_at,
      title: "Complaint recorded",
    });
  }

  if (d.crime_scene?.exists) {
    items.push({
      id: `T-crime-scene`,
      at: d.case.created_at,
      title: "Crime scene report attached",
      description: d.crime_scene.report ?? undefined,
    });

    if (d.crime_scene.is_approved === true) {
      items.push({
        id: `T-crime-scene-approved`,
        at: d.case.created_at,
        title: "Crime scene approved",
      });
    }
  }

  if (d.solve_request?.submitted_at) {
    items.push({
      id: `T-solve-submit`,
      at: d.solve_request.submitted_at,
      title: "Solve request submitted",
      description: d.solve_request.note || undefined,
    });
  }

  if (d.captain_decision?.decided_at) {
    items.push({
      id: `T-captain-decision`,
      at: d.captain_decision.decided_at,
      title: "Captain decision submitted",
      description: d.captain_decision.comment || undefined,
    });
  }

  if (d.trial?.judged_at) {
    items.push({
      id: `T-trial`,
      at: d.trial.judged_at,
      title: "Trial verdict recorded",
      description: d.trial.punishment_title || undefined,
    });
  }

  return items.sort((a, b) => new Date(a.at).getTime() - new Date(b.at).getTime());
}

function buildDecisions(d: BackendDossier): CaseDecision[] {
  const out: CaseDecision[] = [];

  if (d.captain_decision?.decided_at) {
    out.push({
      id: `D-captain`,
      at: d.captain_decision.decided_at,
      by: d.captain_decision.decided_by ? `User #${d.captain_decision.decided_by}` : "Captain",
      decision: d.captain_decision.decision === "SEND_TO_TRIAL" ? "APPROVED" : "REJECTED",
      notes: d.captain_decision.comment || undefined,
    });
  }

  if (d.trial?.judged_at) {
    out.push({
      id: `D-trial`,
      at: d.trial.judged_at,
      by: d.trial.judged_by ? `User #${d.trial.judged_by}` : "Judge",
      decision: d.trial.verdict === "GUILTY" ? "APPROVED" : "REJECTED",
      notes:
        d.trial.punishment_title || d.trial.punishment_description
          ? `${d.trial.punishment_title}${d.trial.punishment_description ? ` — ${d.trial.punishment_description}` : ""}`
          : undefined,
    });
  }

  return out.sort((a, b) => new Date(b.at).getTime() - new Date(a.at).getTime());
}

export async function getCaseDetails(caseId: string): Promise<CaseDetailsBundle | null> {
  const id = normalizeCaseId(caseId);

  try {
    const { data } = await apiClient.get<BackendDossier>(`/cases/${id}/dossier/`);

    const suspectIds = (data.interrogations ?? []).map((x) => `S-${x.suspect_id}`);
    const evidenceIds: string[] = [];

    const details: CaseDetails = {
      id: `C-${data.case.id}`,
      title: data.case.title,
      status: mapStatus(data.case.status),
      complaintType: mapComplaintType(data),
      createdAt: data.case.created_at,
      updatedAt: undefined,
      description:
        data.case.description?.trim() ||
        (typeof data.complaint === "string" ? data.complaint : "") ||
        (data.crime_scene?.report ?? "") ||
        "",
      reporterName: data.case.created_by ? `User #${data.case.created_by}` : undefined,
      reporterContact: undefined,
      assignedDetectiveId: undefined,
      evidenceIds,
      suspectIds,
    };

    return {
      case: details,
      timeline: buildTimeline(data),
      decisions: buildDecisions(data),
    };
  } catch {
    return null;
  }
}
