import { apiClient } from "./apiClient";

export type HomeStats = {
  solvedCases: number;
  totalStaff: number;
  activeCases: number;
};

type BackendStats = Record<string, unknown>;

function num(v: unknown): number {
  return typeof v === "number" && Number.isFinite(v) ? v : 0;
}

export async function getHomeStats(): Promise<HomeStats> {
  const { data } = await apiClient.get<BackendStats>("/stats/");

  const casesClosed =
    num(data.cases_closed) ||
    num(data.casesClosed) ||
    num(data.closed_cases) ||
    0;

  const casesOpen =
    num(data.cases_open) ||
    num(data.casesOpen) ||
    num(data.open_cases) ||
    0;

  return {
    solvedCases: casesClosed,
    totalStaff: 0,
    activeCases: casesOpen,
  };
}
