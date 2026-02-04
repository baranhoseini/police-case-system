import type { PropsWithChildren } from "react";
import { Link } from "react-router-dom";

type Props = PropsWithChildren<{
  title?: string;
}>;

export default function AuthLayout({ title = "Authentication", children }: Props) {
  return (
    <div className="container" style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <div style={{ width: "min(420px, 100%)" }}>
        <Link to="/" style={{ display: "inline-block", marginBottom: 16, color: "var(--muted)" }}>
          ← Back to Home
        </Link>

        <h1 style={{ marginTop: 0 }}>{title}</h1>
        {children}

      </div>
    </div>
  );
}
