import { apiClient } from "./apiClient";
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

type BackendEvidence = {
  id: number;
  evidence_type: string;
  title: string;
  description: string;
  created_at: string;

  image_url: string;
  image_urls: string;
  media_urls: string;

  medical_result: string;

  vehicle_model: string;
  vehicle_color: string;
  plate_number: string;
  serial_number: string;

  id_fields: string;
  transcription: string;

  case: number;
  created_by: number;
};

function normalizeCaseIdToNumber(raw: string): number {
  const trimmed = raw.trim();
  const numeric = trimmed.replace(/^C-/i, "");
  const n = Number(numeric);
  if (!Number.isFinite(n)) throw new Error("Invalid case id");
  return n;
}

function splitUrls(v: string | null | undefined): string[] {
  const s = (v ?? "").trim();
  if (!s) return [];
  try {
    const parsed = JSON.parse(s);
    if (Array.isArray(parsed)) return parsed.map(String).filter(Boolean);
  } catch {
    // ignore
  }
  return s
    .split(/[\s,]+/g)
    .map((x) => x.trim())
    .filter(Boolean);
}

function joinUrls(urls: string[]): string {
  return urls.map((x) => x.trim()).filter(Boolean).join(",");
}

function safeParseObject(v: string | null | undefined): Record<string, string> {
  const s = (v ?? "").trim();
  if (!s) return {};
  try {
    const parsed = JSON.parse(s);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      const out: Record<string, string> = {};
      for (const [k, val] of Object.entries(parsed as Record<string, unknown>)) {
        out[String(k)] = typeof val === "string" ? val : JSON.stringify(val);
      }
      return out;
    }
  } catch {
    // ignore
  }
  return { id_fields: s };
}

function guessKind(x: BackendEvidence): Evidence["kind"] {
  const t = (x.evidence_type ?? "").toUpperCase();

  if (t.includes("VEHICLE") || x.plate_number || x.vehicle_model || x.vehicle_color || x.serial_number)
    return "VEHICLE";

  if (t.includes("MEDICAL") || x.medical_result) return "MEDICAL";

  if (t.includes("ID") || t.includes("IDENTITY") || x.id_fields) return "IDENTITY";

  if (t.includes("MEDIA") || x.image_url || x.image_urls || x.media_urls || x.transcription)
    return "MEDIA";

  return "IDENTITY";
}

function mapFromBackend(x: BackendEvidence): Evidence {
  const kind = guessKind(x);

  const base = {
    id: String(x.id),
    caseId: `C-${String(x.case)}`,
    kind,
    title: x.title,
    description: x.description || undefined,
    status: "PENDING" as EvidenceStatus,
    createdAt: x.created_at,
  } as const;

  if (kind === "VEHICLE") {
    return {
      ...base,
      kind: "VEHICLE",
      plateNumber: x.plate_number || undefined,
      vin: x.serial_number || undefined,
      model: x.vehicle_model || undefined,
      color: x.vehicle_color || undefined,
    };
  }

  if (kind === "MEDICAL") {
    return {
      ...base,
      kind: "MEDICAL",
      sampleType: x.transcription || undefined,
      labNotes: x.medical_result || undefined,
    };
  }

  if (kind === "IDENTITY") {
    return {
      ...base,
      kind: "IDENTITY",
      fields: safeParseObject(x.id_fields),
    };
  }

  const images = splitUrls(x.image_urls);
  const media = splitUrls(x.media_urls);
  const url = x.image_url || images[0] || media[0] || "";

  return {
    ...base,
    kind: "MEDIA",
    mediaType: (x.image_url || images.length > 0 ? "IMAGE" : "VIDEO") as "IMAGE" | "VIDEO" | "AUDIO",
    url,
  };
}

export async function listEvidence(params?: { caseId?: string }): Promise<Evidence[]> {
  const caseId = params?.caseId?.trim();
  const caseParam = caseId ? normalizeCaseIdToNumber(caseId) : null;

  const { data } = await apiClient.get<BackendEvidence[]>("/evidence/", {
    params: caseParam ? { case: caseParam } : undefined,
  });

  return (data ?? []).map(mapFromBackend);
}

export async function addEvidence(input: AddEvidenceInput): Promise<Evidence> {
  const caseNum = normalizeCaseIdToNumber(input.caseId);

  const body: Record<string, unknown> = {
    case: caseNum,
    title: input.title.trim(),
    description: input.description?.trim() || "",
    evidence_type: "GENERIC",
    image_url: "",
    image_urls: "",
    medical_result: "",
    vehicle_model: "",
    vehicle_color: "",
    plate_number: "",
    serial_number: "",
    id_fields: "",
    transcription: "",
    media_urls: "",
  };

  if (input.kind === "IDENTITY") {
    body.id_fields = JSON.stringify(input.fields);
    body.evidence_type = "IDENTITY";
  }

  if (input.kind === "VEHICLE") {
    body.evidence_type = "VEHICLE";
    body.plate_number = input.plateNumber?.trim() || "";
    body.serial_number = input.vin?.trim() || "";
    body.vehicle_model = input.model?.trim() || "";
    body.vehicle_color = input.color?.trim() || "";
  }

  if (input.kind === "MEDICAL") {
    body.evidence_type = "MEDICAL";
    body.medical_result = input.labNotes?.trim() || "";
    body.transcription = input.sampleType?.trim() || "";
  }

  if (input.kind === "MEDIA") {
    body.evidence_type = "MEDIA";
    if (input.mediaType === "IMAGE") {
      body.image_url = input.url.trim();
      body.image_urls = joinUrls([input.url.trim()]);
    } else {
      body.media_urls = joinUrls([input.url.trim()]);
    }
  }

  const { data } = await apiClient.post<BackendEvidence>("/evidence/", body);
  return mapFromBackend(data);
}

export async function setEvidenceStatus(id: string, status: EvidenceStatus): Promise<void> {
  void id;
  void status;
  throw new Error("Evidence status update is not supported by the backend yet.");
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
