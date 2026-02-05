export type HomeStats = {
  solvedCases: number;
  totalStaff: number;
  activeCases: number;
};

export async function getHomeStats(): Promise<HomeStats> {
  // Later: replace with API call (apiClient.get("/stats/home"))
  await new Promise((r) => setTimeout(r, 250));

  return {
    solvedCases: 128,
    totalStaff: 42,
    activeCases: 17,
  };
}
