import type { PropsWithChildren } from "react";
import { Link } from "react-router-dom";

type Props = PropsWithChildren<{
  title?: string;
}>;

export default function MainLayout({ title, children }: Props) {
  return (
    <div>
      {/* Top navbar */}
      <header
        style={{
          borderBottom: "1px solid var(--border)",
          background: "white",
        }}
      >
        <div
          className="container"
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            paddingTop: 14,
            paddingBottom: 14,
          }}
        >
          <Link to="/" style={{ fontWeight: 800 }}>
            Police Case System
          </Link>

          <nav style={{ display: "flex", gap: 14, color: "var(--muted)" }}>
            <Link to="/">Home</Link>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/auth">Sign in</Link>
          </nav>
        </div>
      </header>

      {/* Body with sidebar + content */}
      <div className="container" style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: 18 }}>
        <aside
          style={{
            border: "1px solid var(--border)",
            borderRadius: 14,
            padding: 14,
            background: "white",
            height: "fit-content",
            position: "sticky",
            top: 16,
          }}
        >
          <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 8 }}>Navigation</div>

          <div style={{ display: "grid", gap: 10 }}>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/cases">Cases</Link>
            <Link to="/evidence">Evidence</Link>
            <Link to="/detective-board">Detective Board</Link>
            <Link to="/most-wanted">Most Wanted</Link>
          </div>
        </aside>

        <main style={{ minWidth: 0 }}>
          {title ? <h1 style={{ marginTop: 0 }}>{title}</h1> : null}
          {children}
        </main>
      </div>
    </div>
  );
}
