import { apiClient } from "./apiClient";
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

function normalizeCaseId(v: string): string {
  return v.trim().replace(/^C-/i, "");
}

function mapStatus(s: BackendCase["status"]): CaseStatus {
  if (s === "OPEN") return "ACTIVE";
  if (s === "INVALIDATED") return "REJECTED";
  return s;
}

function mapComplaintType(_d: BackendDossier): ComplaintType {
  return "OTHER";
}

function buildTimeline(d: BackendDossier): CaseStatusTimelineItem[] {
  const items: CaseStatusTimelineItem[] = [];

  const createdStatus = mapStatus(d.case.status);

  items.push({
    at: d.case.created_at,
    status: createdStatus,
    title: "Case created",
  });

  if (typeof d.complaint === "string" && d.complaint.trim()) {
    items.push({
      at: d.case.created_at,
      status: createdStatus,
      title: "Complaint recorded",
    });
  }

  if (d.crime_scene?.exists) {
    items.push({
      at: d.case.created_at,
      status: createdStatus,
      title: "Crime scene report attached",
      description: d.crime_scene.report ?? undefined,
    });

    if (d.crime_scene.is_approved === true) {
      items.push({
        at: d.case.created_at,
        status: createdStatus,
        title: "Crime scene approved",
      });
    }
  }

  if (d.solve_request?.submitted_at) {
    items.push({
      at: d.solve_request.submitted_at,
      status: createdStatus,
      title: "Solve request submitted",
      description: d.solve_request.note || undefined,
    });
  }

  if (d.captain_decision?.decided_at) {
    items.push({
      at: d.captain_decision.decided_at,
      status: createdStatus,
      title: "Captain decision recorded",
      description: d.captain_decision.comment || undefined,
    });

    if (d.captain_decision.chief_at) {
      items.push({
        at: d.captain_decision.chief_at,
        status: createdStatus,
        title: "Chief review",
        description: d.captain_decision.chief_comment || undefined,
      });
    }
  }

  if (d.trial?.judged_at) {
    const punishment =
      d.trial.punishment_title || d.trial.punishment_description
        ? `${d.trial.punishment_title}${d.trial.punishment_description ? ` — ${d.trial.punishment_description}` : ""}`
        : undefined;

    items.push({
      at: d.trial.judged_at,
      status: createdStatus,
      title: d.trial.verdict === "GUILTY" ? "Trial verdict: Guilty" : "Trial verdict: Innocent",
      description: punishment,
    });
  }

  return items.sort((a, b) => new Date(a.at).getTime() - new Date(b.at).getTime());
}

export async function trackCaseStatus(caseIdOrCode: string): Promise<CaseStatusResult | null> {
  const id = normalizeCaseId(caseIdOrCode);
  if (!id) return null;

  try {
    const { data } = await apiClient.get<BackendDossier>(`/cases/${id}/dossier/`);

    const currentStatus = mapStatus(data.case.status);

    return {
      caseId: `C-${data.case.id}`,
      title: data.case.title,
      complaintType: mapComplaintType(data),
      currentStatus,
      createdAt: data.case.created_at,
      updatedAt: undefined,
      timeline: buildTimeline(data),
    };
  } catch {
    return null;
  }
}
