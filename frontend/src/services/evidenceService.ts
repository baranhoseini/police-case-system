import type { Evidence, EvidenceStatus, IdentityEvidence, MedicalEvidence, MediaEvidence, VehicleEvidence } from "../types/evidence";

let store: Evidence[] = [
  {
    id: "E-3001",
    caseId: "C-1001",
    kind: "MEDIA",
    title: "CCTV snapshot",
    description: "Still image from station camera",
    status: "PENDING",
    createdAt: "2026-02-02T10:10:00Z",
    mediaType: "IMAGE",
    url: "https://example.com/cctv.jpg",
  },
  {
    id: "E-3002",
    caseId: "C-1001",
    kind: "IDENTITY",
    title: "Witness identity",
    status: "VERIFIED",
    createdAt: "2026-02-02T10:30:00Z",
    fields: { "National ID": "X1234567", Name: "Anonymous witness" },
  },
];

function genId() {
  return `E-${Math.floor(1000 + Math.random() * 9000)}`;
}

export async function listEvidence(params?: { caseId?: string }): Promise<Evidence[]> {
  await new Promise((r) => setTimeout(r, 200));
  if (params?.caseId) return store.filter((e) => e.caseId === params.caseId);
  return [...store];
}

export async function addEvidence(e: Omit<Evidence, "id" | "createdAt" | "status">): Promise<Evidence> {
  await new Promise((r) => setTimeout(r, 200));
  const created: Evidence = {
    ...(e as Evidence),
    id: genId(),
    createdAt: new Date().toISOString(),
    status: "PENDING",
  };
  store = [created, ...store];
  return created;
}

export async function setEvidenceStatus(id: string, status: EvidenceStatus): Promise<void> {
  await new Promise((r) => setTimeout(r, 150));
  store = store.map((e) => (e.id === id ? { ...e, status } : e));
}

export function formatEvidenceKind(kind: Evidence["kind"]): string {
  const map: Record<Evidence["kind"], string> = {
    IDENTITY: "Identity",
    VEHICLE: "Vehicle",
    MEDICAL: "Medical",
    MEDIA: "Media",
  };
  return map[kind];
}

export function formatEvidenceStatus(s: EvidenceStatus): string {
  const map: Record<EvidenceStatus, string> = {
    PENDING: "Pending",
    VERIFIED: "Verified",
    REJECTED: "Rejected",
  };
  return map[s];
}
