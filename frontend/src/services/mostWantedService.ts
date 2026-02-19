import { apiClient } from "./apiClient";
import type { MostWantedItem, MostWantedLevel } from "../types/mostWanted";

type BackendMostWanted = {
  id: number;
  full_name: string;
  chase_started_at: string;
  rank_score?: number;
  reward_amount_rials?: number;
};

function levelFromScore(score: number): MostWantedLevel {
  if (score >= 80) return "CRITICAL";
  if (score >= 40) return "HIGH";
  if (score >= 20) return "MEDIUM";
  return "LOW";
}

export async function listMostWanted(): Promise<MostWantedItem[]> {
  const { data } = await apiClient.get<BackendMostWanted[]>("/suspects/most-wanted/");

  return data.map((s) => ({
    id: String(s.id),
    fullName: s.full_name,
    reason: "—",
    level: levelFromScore(typeof s.rank_score === "number" ? s.rank_score : 0),
    rewardAmount: typeof s.reward_amount_rials === "number" ? s.reward_amount_rials : 0,
    lastSeenLocation: undefined,
    createdAt: s.chase_started_at,
  }));
}

export function formatMostWantedLevel(level: MostWantedLevel): string {
  const map: Record<MostWantedLevel, string> = {
    LOW: "Low",
    MEDIUM: "Medium",
    HIGH: "High",
    CRITICAL: "Critical",
  };
  return map[level];
}
