import type { PropsWithChildren } from "react";

export default function Table({ children }: PropsWithChildren) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>{children}</table>
    </div>
  );
}

export function Th({ children }: PropsWithChildren) {
  return (
    <th
      style={{
        textAlign: "left",
        fontSize: 12,
        color: "var(--muted)",
        padding: "10px 10px",
        borderBottom: "1px solid var(--border)",
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </th>
  );
}

export function Td({ children }: PropsWithChildren) {
  return (
    <td style={{ padding: "12px 10px", borderBottom: "1px solid var(--border)" }}>{children}</td>
  );
}
