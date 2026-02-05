import type { Evidence, EvidenceStatus } from "../types/evidence";

type AddIdentityEvidenceInput = {
  kind: "IDENTITY";
  caseId: string;
  title: string;
  description?: string;
  fields: Record<string, string>;
};

type AddVehicleEvidenceInput = {
  kind: "VEHICLE";
  caseId: string;
  title: string;
  description?: string;
  plateNumber?: string;
  vin?: string;
  model?: string;
  color?: string;
};

type AddMedicalEvidenceInput = {
  kind: "MEDICAL";
  caseId: string;
  title: string;
  description?: string;
  sampleType?: string;
  labNotes?: string;
};

type AddMediaEvidenceInput = {
  kind: "MEDIA";
  caseId: string;
  title: string;
  description?: string;
  mediaType: "IMAGE" | "VIDEO" | "AUDIO";
  url: string;
};

export type AddEvidenceInput =
  | AddIdentityEvidenceInput
  | AddVehicleEvidenceInput
  | AddMedicalEvidenceInput
  | AddMediaEvidenceInput;

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

export async function addEvidence(input: AddEvidenceInput): Promise<Evidence> {
  await new Promise((r) => setTimeout(r, 200));

  const base = {
    id: genId(),
    caseId: input.caseId,
    title: input.title,
    description: input.description,
    createdAt: new Date().toISOString(),
    status: "PENDING" as const,
  };

  let created: Evidence;

  switch (input.kind) {
    case "IDENTITY":
      created = { ...base, kind: "IDENTITY", fields: input.fields };
      break;
    case "VEHICLE":
      created = {
        ...base,
        kind: "VEHICLE",
        plateNumber: input.plateNumber,
        vin: input.vin,
        model: input.model,
        color: input.color,
      };
      break;
    case "MEDICAL":
      created = { ...base, kind: "MEDICAL", sampleType: input.sampleType, labNotes: input.labNotes };
      break;
    case "MEDIA":
      created = { ...base, kind: "MEDIA", mediaType: input.mediaType, url: input.url };
      break;
  }

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
