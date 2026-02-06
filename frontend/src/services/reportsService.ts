import type { CaseReport } from "../types/report";

export async function generateCaseReport(caseId: string): Promise<CaseReport> {
  await new Promise((r) => setTimeout(r, 300));

  return {
    id: `R-${Date.now()}`,
    generatedAt: new Date().toISOString(),
    generatedBy: { id: "U-1", fullName: "System User", role: "DETECTIVE" },
    notes: "This is a mock report preview. API integration will replace this later.",
    case: {
      id: caseId,
      title: "Mock case title",
      status: "UNDER_REVIEW",
      complaintType: "FRAUD",
      createdAt: "2026-02-01T09:00:00Z",
      updatedAt: new Date().toISOString(),
      description: "Mock case description for reporting preview.",
      reporterName: "Mock Reporter",
      reporterContact: "—",
      assignedDetectiveId: "U-22",
      evidenceIds: ["E-3001", "E-3002"],
      suspectIds: ["S-9001"],
    },
    evidence: [],
    involvedUsers: [],
    mostWanted: [],
  };
}
