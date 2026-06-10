import { apiClient } from "./apiClient";

export type ComplaintStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "UNDER_REVIEW"
  | "OPEN"
  | "CLOSED"
  | "INVALIDATED"
  | string;

export type ComplaintItem = {
  id: number;
  title: string;
  status: ComplaintStatus;
  createdAt: string;
  updatedAt?: string;
};

type BackendComplaint = {
  id: number;
  title?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
  description?: string;
  payload?: Record<string, unknown>;
} & Record<string, unknown>;

function mapComplaint(x: BackendComplaint): ComplaintItem {
  const payloadTitle = typeof x.payload?.title === "string" ? x.payload.title : "";
  const title =
    (typeof x.title === "string" && x.title.trim() ? x.title : "") ||
    (payloadTitle.trim() ? payloadTitle : `Complaint #${x.id}`);
  const status = typeof x.status === "string" ? x.status : "SUBMITTED";
  const createdAt = typeof x.created_at === "string" ? x.created_at : new Date().toISOString();
  const updatedAt = typeof x.updated_at === "string" ? x.updated_at : undefined;

  return { id: x.id, title, status, createdAt, updatedAt };
}

export async function listComplaints(): Promise<ComplaintItem[]> {
  const { data } = await apiClient.get<BackendComplaint[]>("/intake/complaints/");
  return (data ?? []).map(mapComplaint);
}

export async function listCadetInbox(): Promise<ComplaintItem[]> {
  const { data } = await apiClient.get<BackendComplaint[]>("/intake/complaints/cadet_inbox/");
  return (data ?? []).map(mapComplaint);
}

export async function listOfficerInbox(): Promise<ComplaintItem[]> {
  const { data } = await apiClient.get<BackendComplaint[]>("/intake/complaints/officer_inbox/");
  return (data ?? []).map(mapComplaint);
}

export async function getComplaint(id: number): Promise<BackendComplaint> {
  const { data } = await apiClient.get<BackendComplaint>(`/intake/complaints/${id}/`);
  return data;
}

export async function createComplaint(body: Record<string, unknown>): Promise<BackendComplaint> {
  const { data } = await apiClient.post<BackendComplaint>("/intake/complaints/", body);
  return data;
}

export async function updateComplaint(id: number, body: Record<string, unknown>): Promise<BackendComplaint> {
  const { data } = await apiClient.put<BackendComplaint>(`/intake/complaints/${id}/`, body);
  return data;
}

export async function patchComplaint(id: number, body: Record<string, unknown>): Promise<BackendComplaint> {
  const { data } = await apiClient.patch<BackendComplaint>(`/intake/complaints/${id}/`, body);
  return data;
}

export async function deleteComplaint(id: number): Promise<void> {
  await apiClient.delete(`/intake/complaints/${id}/`);
}


// Intake review endpoints use different status enums for Cadet vs Officer.
// Cadet: {status: "approve" | "request_changes", error_message?: string}
// Officer: {status: "approve" | "defect", error_message?: string}

function normalizeCadetReviewBody(
  body: Record<string, unknown> | null | undefined,
  opts?: { requestChanges?: boolean; errorMessage?: string },
) {
  if (opts?.requestChanges) {
    return { status: "request_changes", error_message: (opts.errorMessage ?? "").trim() };
  }
  const b = body ?? {};
  const status = typeof b.status === "string" ? b.status : "";
  if (status === "approve" || status === "request_changes") return b;
  return { status: "approve" };
}

function normalizeOfficerReviewBody(
  body: Record<string, unknown> | null | undefined,
  opts?: { defect?: boolean; errorMessage?: string },
) {
  if (opts?.defect) {
    return { status: "defect", error_message: (opts.errorMessage ?? "").trim() };
  }
  const b = body ?? {};
  const status = typeof b.status === "string" ? b.status : "";
  if (status === "approve" || status === "defect") return b;
  return { status: "approve" };
}

export async function cadetReview(id: number, body?: Record<string, unknown>): Promise<BackendComplaint> {
  const payload = normalizeCadetReviewBody(body);
  const { data } = await apiClient.post<BackendComplaint>(`/intake/complaints/${id}/cadet_review/`, payload);
  return data;
}

export async function cadetReject(id: number, errorMessage: string): Promise<BackendComplaint> {
  const payload = normalizeCadetReviewBody(null, { requestChanges: true, errorMessage });
  const { data } = await apiClient.post<BackendComplaint>(`/intake/complaints/${id}/cadet_review/`, payload);
  return data;
}

export async function officerReview(id: number, body?: Record<string, unknown>): Promise<BackendComplaint> {
  const payload = normalizeOfficerReviewBody(body);
  const { data } = await apiClient.post<BackendComplaint>(`/intake/complaints/${id}/officer_review/`, payload);
  return data;
}

export async function officerReject(id: number, errorMessage: string): Promise<BackendComplaint> {
  const payload = normalizeOfficerReviewBody(null, { defect: true, errorMessage });
  const { data } = await apiClient.post<BackendComplaint>(`/intake/complaints/${id}/officer_review/`, payload);
  return data;
}

export async function resubmitComplaint(id: number, body: Record<string, unknown> = {}): Promise<BackendComplaint> {
  const { data } = await apiClient.post<BackendComplaint>(`/intake/complaints/${id}/resubmit/`, body);
  return data;
}
