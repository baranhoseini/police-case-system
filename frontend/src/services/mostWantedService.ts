import type { MostWantedItem, MostWantedLevel } from "../types/mostWanted";

const MOCK: MostWantedItem[] = [
  {
    id: "MW-2001",
    fullName: "Daniel Kraus",
    reason: "Armed robbery and repeated assault",
    level: "CRITICAL",
    rewardAmount: 25000,
    lastSeenLocation: "Berlin, Friedrichshain",
    createdAt: "2026-01-22T09:00:00Z",
  },
  {
    id: "MW-2002",
    fullName: "Mila Novak",
    reason: "Major fraud network coordinator",
    level: "HIGH",
    rewardAmount: 15000,
    lastSeenLocation: "Hamburg, Altona",
    createdAt: "2026-01-29T12:20:00Z",
  },
  {
    id: "MW-2003",
    fullName: "Omar Haddad",
    reason: "Vehicle theft ring involvement",
    level: "MEDIUM",
    rewardAmount: 8000,
    lastSeenLocation: "Cologne, Innenstadt",
    createdAt: "2026-02-02T16:10:00Z",
  },
  {
    id: "MW-2004",
    fullName: "Lea Schuster",
    reason: "Repeated cyber crime and identity theft",
    level: "LOW",
    rewardAmount: 3000,
    lastSeenLocation: "Munich, Schwabing",
    createdAt: "2026-02-04T08:40:00Z",
  },
];

export async function listMostWanted(): Promise<MostWantedItem[]> {
  await new Promise((r) => setTimeout(r, 250));
  return [...MOCK];
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
