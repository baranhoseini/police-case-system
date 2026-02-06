import type { ReactNode } from "react";

type Props = {
  title: string;
  description?: string;
  action?: ReactNode;
};

export default function EmptyState({ title, description, action }: Props) {
  return (
    <div
      style={{
        border: "1px dashed var(--border)",
        borderRadius: 14,
        padding: 14,
        background: "white",
        display: "grid",
        gap: 8,
      }}
    >
      <div style={{ fontWeight: 900 }}>{title}</div>
      {description ? <div style={{ color: "var(--muted)", fontSize: 13 }}>{description}</div> : null}
      {action ? <div style={{ marginTop: 6 }}>{action}</div> : null}
    </div>
  );
}
