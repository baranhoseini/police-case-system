import type { ID, ISODateString } from "./common";

export type MostWantedLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type MostWantedItem = {
  id: ID;
  fullName: string;
  reason: string;
  level: MostWantedLevel;
  rewardAmount: number;
  lastSeenLocation?: string;
  createdAt: ISODateString;
};
