import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import Card from "../components/Card";
import Input from "../components/Input";
import MainLayout from "../components/layout/MainLayout";
import { useAuth } from "../features/auth/useAuth";
import { canAccessModule } from "../features/auth/permissions";
import { MODULES } from "../features/modules/moduleRegistry";

export default function DashboardPage() {
  const { role } = useAuth();
  const [q, setQ] = useState("");

  const visibleModules = useMemo(() => {
    if (!role) return [];
    const allowed = MODULES.filter((m) => canAccessModule(role, m.key));
    const query = q.trim().toLowerCase();
    if (!query) return allowed;

    return allowed.filter(
      (m) => m.title.toLowerCase().includes(query) || m.description.toLowerCase().includes(query),
    );
  }, [role, q]);

  return (
    <MainLayout title="Dashboard">
      <div style={{ display: "grid", gap: 14 }}>
        <Card title="Your access">
          <p style={{ marginTop: 0, color: "var(--muted)" }}>
            Current role: <strong>{role ?? "Unknown"}</strong>
          </p>
        </Card>

        <Card title="Modules">
          <div style={{ display: "grid", gap: 12 }}>
            <Input
              label="Search modules"
              placeholder="Type to search..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />

            {role && visibleModules.length === 0 ? (
              <p style={{ margin: 0, color: "var(--muted)" }}>No modules match your search.</p>
            ) : null}

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
                gap: 14,
              }}
            >
              {visibleModules.map((m) => (
                <Card key={m.key} title={m.title}>
                  <p style={{ marginTop: 0, color: "var(--muted)" }}>{m.description}</p>
                  <Link to={m.to} style={{ fontWeight: 800 }}>
                    Open →
                  </Link>
                </Card>
              ))}
            </div>
          </div>
        </Card>
      </div>
    </MainLayout>
  );
}