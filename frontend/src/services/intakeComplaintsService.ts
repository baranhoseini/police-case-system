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
} & Record<string, unknown>;

function mapComplaint(x: BackendComplaint): ComplaintItem {
  const title = typeof x.title === "string" && x.title.trim() ? x.title : `Complaint #${x.id}`;
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

export async function cadetReview(id: number, body: Record<string, unknown> = {}): Promise<BackendComplaint> {
  const { data } = await apiClient.post<BackendComplaint>(`/intake/complaints/${id}/cadet_review/`, body);
  return data;
}

export async function officerReview(id: number, body: Record<string, unknown> = {}): Promise<BackendComplaint> {
  const { data } = await apiClient.post<BackendComplaint>(`/intake/complaints/${id}/officer_review/`, body);
  return data;
}

export async function resubmitComplaint(id: number, body: Record<string, unknown> = {}): Promise<BackendComplaint> {
  const { data } = await apiClient.post<BackendComplaint>(`/intake/complaints/${id}/resubmit/`, body);
  return data;
}
