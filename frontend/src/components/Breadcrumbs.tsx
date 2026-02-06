import { Link } from "react-router-dom";

type Crumb = {
  label: string;
  to?: string;
};

export default function Breadcrumbs({ items }: { items: Crumb[] }) {
  return (
    <nav aria-label="Breadcrumb" style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        {items.map((c, idx) => {
          const last = idx === items.length - 1;

          return (
            <div key={`${c.label}-${idx}`} style={{ display: "flex", gap: 8, alignItems: "center" }}>
              {c.to && !last ? (
                <Link to={c.to} style={{ fontWeight: 800 }}>
                  {c.label}
                </Link>
              ) : (
                <span style={{ fontWeight: last ? 900 : 700, color: last ? "var(--primary)" : "var(--muted)" }}>
                  {c.label}
                </span>
              )}
              {!last ? <span style={{ color: "var(--muted)" }}>/</span> : null}
            </div>
          );
        })}
      </div>
    </nav>
  );
}
