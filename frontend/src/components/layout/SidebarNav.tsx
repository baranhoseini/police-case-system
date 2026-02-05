import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../features/auth/AuthContext";
import { canAccessModule } from "../../features/auth/permissions";
import { MODULES } from "../../features/modules/moduleRegistry";

export default function SidebarNav() {
  const { role } = useAuth();
  const location = useLocation();

  const visible = role ? MODULES.filter((m) => canAccessModule(role, m.key)) : [];

  return (
    <div style={{ display: "grid", gap: 10 }}>
      {visible.map((m) => {
        const active = location.pathname === m.to;
        return (
          <Link
            key={m.key}
            to={m.to}
            style={{
              padding: "8px 10px",
              borderRadius: 10,
              border: "1px solid var(--border)",
              background: active ? "var(--bg-muted)" : "white",
              fontWeight: active ? 800 : 600,
              color: "var(--primary)",
            }}
          >
            {m.title}
          </Link>
        );
      })}
    </div>
  );
}
