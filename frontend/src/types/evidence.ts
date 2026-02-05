import type { ID, ISODateString } from "./common";

export type EvidenceStatus = "PENDING" | "VERIFIED" | "REJECTED";

export type EvidenceBase = {
  id: ID;
  caseId: ID;
  title: string;
  description?: string;
  status: EvidenceStatus;
  createdAt: ISODateString;
  createdByUserId?: ID;
};

/**
 * A) Identity evidence as key-value pairs (e.g. National ID, Passport, etc.)
 */
export type IdentityEvidence = EvidenceBase & {
  kind: "IDENTITY";
  fields: Record<string, string>;
};

/**
 * B) Vehicle evidence
 */
export type VehicleEvidence = EvidenceBase & {
  kind: "VEHICLE";
  plateNumber?: string;
  vin?: string;
  model?: string;
  color?: string;
};

/**
 * C) Biological / Medical evidence
 */
export type MedicalEvidence = EvidenceBase & {
  kind: "MEDICAL";
  sampleType?: string; // e.g. blood, hair
  labNotes?: string;
};

/**
 * D) Media evidence (image/video/audio)
 */
export type MediaEvidence = EvidenceBase & {
  kind: "MEDIA";
  mediaType: "IMAGE" | "VIDEO" | "AUDIO";
  url: string;
};

export type Evidence = IdentityEvidence | VehicleEvidence | MedicalEvidence | MediaEvidence;
