import type { CSSProperties } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../features/auth/useAuth";
import { canAccessModule } from "../../features/auth/permissions";
import { MODULES } from "../../features/modules/moduleRegistry";

export default function SidebarNav() {
  const { primaryRole, roles } = useAuth();
  const location = useLocation();

  const visible = MODULES.filter((m) => {
    if (canAccessModule(primaryRole, m.key)) return true;
    return (roles ?? []).some((r) => canAccessModule(r, m.key));
  });

  return (
    <div style={{ display: "grid", gap: 10 }}>
      {visible.map((m) => {
        const isExternal = /^https?:\/\//i.test(m.to);
        const active = !isExternal && (location.pathname === m.to || location.pathname.startsWith(`${m.to}/`));

        const commonStyle: CSSProperties = {
          padding: "8px 10px",
          borderRadius: 10,
          border: "1px solid var(--border)",
          background: active ? "var(--bg-muted)" : "white",
          fontWeight: active ? 800 : 600,
          color: "var(--primary)",
        };

        return isExternal ? (
          <a key={m.key} href={m.to} target="_blank" rel="noreferrer" style={commonStyle}>
            {m.title}
          </a>
        ) : (
          <Link key={m.key} to={m.to} style={commonStyle}>
            {m.title}
          </Link>
        );
      })}
    </div>
  );
}
