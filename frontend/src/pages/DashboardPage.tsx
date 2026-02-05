import { Link } from "react-router-dom";
import Card from "../components/Card";
import MainLayout from "../components/layout/MainLayout";
import { useAuth } from "../features/auth/AuthContext";
import { canAccessModule, type AppModuleKey } from "../features/auth/permissions";

type ModuleCard = {
  key: AppModuleKey;
  title: string;
  description: string;
  to: string;
};

const ALL_MODULES: ModuleCard[] = [
  { key: "CASES", title: "Cases", description: "Browse and manage cases.", to: "/cases" },
  { key: "EVIDENCE", title: "Evidence", description: "Register and review evidence.", to: "/evidence" },
  { key: "DETECTIVE_BOARD", title: "Detective Board", description: "Connect clues and visualize links.", to: "/detective-board" },
  { key: "CASE_STATUS", title: "Case Status", description: "Track the status of cases and complaints.", to: "/case-status" },
  { key: "REPORTS", title: "Reports", description: "Generate global case reports.", to: "/reports" },
  { key: "MOST_WANTED", title: "Most Wanted", description: "Severe tracking list and rewards.", to: "/most-wanted" },
  { key: "ADMIN", title: "Admin", description: "Manage users, roles, and settings.", to: "/admin" },
];

export default function DashboardPage() {
  const { role, setRole } = useAuth();

  return (
    <MainLayout title="Dashboard">
      <div style={{ display: "grid", gap: 14 }}>
        <Card title="Your access">
          <p style={{ marginTop: 0, color: "var(--muted)" }}>
            Current role: <strong>{role ?? "Unknown"}</strong>
          </p>

          {/* فقط برای تست: بعداً حذف می‌کنیم */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            {(["CITIZEN", "POLICE_OFFICER", "DETECTIVE", "CAPTAIN", "JUDGE", "CHIEF", "ADMIN"] as const).map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => setRole(r)}
                style={{
                  border: "1px solid var(--border)",
                  padding: "8px 10px",
                  borderRadius: 10,
                  cursor: "pointer",
                  background: "white",
                  fontWeight: 700,
                }}
              >
                {r}
              </button>
            ))}
          </div>
        </Card>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 14 }}>
          {ALL_MODULES.filter((m) => (role ? canAccessModule(role, m.key) : false)).map((m) => (
            <Card key={m.key} title={m.title}>
              <p style={{ marginTop: 0, color: "var(--muted)" }}>{m.description}</p>
              <Link to={m.to} style={{ fontWeight: 800 }}>
                Open →
              </Link>
            </Card>
          ))}
        </div>
      </div>
    </MainLayout>
  );
}
