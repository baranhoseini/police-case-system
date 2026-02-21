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
  vin?: string; // mapped to serial_number when plate is empty
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
  imageUrl?: string; // required by backend validation
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
  evidence_type: "GENERIC" | "MEDICAL" | "VEHICLE" | "ID_DOC" | "WITNESS";
  title: string;
  description: string;
  created_at: string;

  image_url: string;
  image_urls: string[];
  media_urls: string[];

  medical_result: string;

  vehicle_model: string;
  vehicle_color: string;
  plate_number: string;
  serial_number: string;

  id_fields: Record<string, string>;
  transcription: string;

  case: number;
  created_by: number;
};

function normalizeCaseIdToNumber(raw: string): number {
  const n = Number(raw.trim());
  if (!Number.isFinite(n) || n <= 0) throw new Error("Invalid case id (must be a number)");
  return n;
}

function toEvidenceStatus(): EvidenceStatus {
  // Backend model doesn't have verification states; keep UI consistent.
  return "PENDING";
}

function mapFromBackend(b: BackendEvidence): Evidence {
  const base = {
    id: String(b.id),
    caseId: String(b.case),
    title: b.title,
    description: b.description || undefined,
    status: toEvidenceStatus(),
    createdAt: b.created_at,
    createdByUserId: b.created_by ? String(b.created_by) : undefined,
  };

  if (b.evidence_type === "ID_DOC") {
    return { ...base, kind: "IDENTITY", fields: b.id_fields || {} };
  }

  if (b.evidence_type === "VEHICLE") {
    return {
      ...base,
      kind: "VEHICLE",
      plateNumber: b.plate_number || undefined,
      vin: b.serial_number || undefined,
      model: b.vehicle_model || undefined,
      color: b.vehicle_color || undefined,
    };
  }

  if (b.evidence_type === "MEDICAL") {
    // sampleType/labNotes aren't modeled separately in backend; keep them in description.
    return { ...base, kind: "MEDICAL" };
  }

  // WITNESS + GENERIC both map to MEDIA in UI
  const url = (b.media_urls && b.media_urls[0]) || b.image_url || (b.image_urls && b.image_urls[0]) || "";
  return { ...base, kind: "MEDIA", mediaType: "IMAGE", url };
}

function mapToBackend(input: AddEvidenceInput): Partial<BackendEvidence> & { case: number } {
  const caseId = normalizeCaseIdToNumber(input.caseId);

  if (input.kind === "IDENTITY") {
    return {
      case: caseId,
      evidence_type: "ID_DOC",
      title: input.title,
      description: input.description || "",
      id_fields: input.fields || {},
      image_urls: [],
      media_urls: [],
    } as any;
  }

  if (input.kind === "VEHICLE") {
    const plate = (input.plateNumber || "").trim();
    const serial = (input.vin || "").trim();

    return {
      case: caseId,
      evidence_type: "VEHICLE",
      title: input.title,
      description: input.description || "",
      plate_number: plate,
      serial_number: plate ? "" : serial, // enforce backend validation rule
      vehicle_model: input.model || "",
      vehicle_color: input.color || "",
      image_urls: [],
      media_urls: [],
      id_fields: {},
    } as any;
  }

  if (input.kind === "MEDICAL") {
    const img = (input.imageUrl || "").trim();
    return {
      case: caseId,
      evidence_type: "MEDICAL",
      title: input.title,
      description:
        [input.description, input.sampleType ? `Sample: ${input.sampleType}` : "", input.labNotes ? `Lab: ${input.labNotes}` : ""]
          .filter(Boolean)
          .join("\n"),
      image_url: img,
      image_urls: img ? [img] : [],
      media_urls: [],
      id_fields: {},
    } as any;
  }

  // MEDIA
  const url = input.url.trim();
  if (input.mediaType === "IMAGE") {
    return {
      case: caseId,
      evidence_type: "GENERIC",
      title: input.title,
      description: input.description || "",
      image_url: url,
      image_urls: url ? [url] : [],
      media_urls: [],
      id_fields: {},
    } as any;
  }

  // audio/video -> witness to satisfy validation (transcription OR media_urls)
  return {
    case: caseId,
    evidence_type: "WITNESS",
    title: input.title,
    description: input.description || "",
    transcription: "",
    media_urls: url ? [url] : [],
    image_urls: [],
    id_fields: {},
  } as any;
}

export async function listEvidence(opts: { caseId?: string }): Promise<Evidence[]> {
  const params: any = {};
  if (opts.caseId) params.case = normalizeCaseIdToNumber(opts.caseId);
  const { data } = await apiClient.get<BackendEvidence[]>("/evidence/", { params });
  return (data || []).map(mapFromBackend);
}

export async function addEvidence(input: AddEvidenceInput): Promise<Evidence> {
  const body = mapToBackend(input);
  const { data } = await apiClient.post<BackendEvidence>("/evidence/", body);
  return mapFromBackend(data);
}

/**
 * UI-only status changes - backend doesn't track PENDING/VERIFIED/REJECTED yet.
 * Keeping this for UI completeness; no-op on backend.
 */
export async function setEvidenceStatus(_id: string, _status: EvidenceStatus): Promise<void> {
  return;
}

export function formatEvidenceKind(kind: Evidence["kind"]): string {
  if (kind === "IDENTITY") return "Identity";
  if (kind === "VEHICLE") return "Vehicle";
  if (kind === "MEDICAL") return "Medical/Biological";
  return "Media/Other";
}

export function formatEvidenceStatus(status: EvidenceStatus): string {
  if (status === "VERIFIED") return "Verified";
  if (status === "REJECTED") return "Rejected";
  return "Pending";
}
