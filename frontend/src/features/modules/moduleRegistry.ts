import type { AppModuleKey } from "../auth/permissions";

export type ModuleInfo = {
  key: AppModuleKey;
  title: string;
  description: string;
  to: string;
};

export const MODULES: ModuleInfo[] = [
  { key: "CASES", title: "Cases", description: "Browse and manage cases.", to: "/cases" },
  {
    key: "EVIDENCE",
    title: "Evidence",
    description: "Register and review evidence.",
    to: "/evidence",
  },
  {
    key: "DETECTIVE_BOARD",
    title: "Detective Board",
    description: "Connect clues and visualize links.",
    to: "/detective-board",
  },
  {
    key: "CASE_STATUS",
    title: "Case Status",
    description: "Track the status of cases and complaints.",
    to: "/case-status",
  },
  {
    key: "REPORTS",
    title: "Reports",
    description: "Generate global case reports.",
    to: "/reports",
  },
  {
    key: "MOST_WANTED",
    title: "Most Wanted",
    description: "Severe tracking list and rewards.",
    to: "/most-wanted",
  },
  { key: "ADMIN", title: "Admin", description: "Manage users, roles, and settings.", to: "/admin" },
];
