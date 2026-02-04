import type { PropsWithChildren } from "react";

type Props = PropsWithChildren<{
  title?: string;
}>;

export default function Card({ title, children }: Props) {
  return (
    <section
      style={{
        border: "1px solid var(--border)",
        borderRadius: 14,
        padding: 16,
        background: "var(--bg-muted)",
      }}
    >
      {title ? <h2 style={{ margin: "0 0 12px 0" }}>{title}</h2> : null}
      {children}
    </section>
  );
}
