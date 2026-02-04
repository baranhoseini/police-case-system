import type { InputHTMLAttributes } from "react";

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string;
};

export default function Input({ label, error, style, ...props }: Props) {
  return (
    <label style={{ display: "grid", gap: 6 }}>
      {label ? <span style={{ fontSize: 14, color: "var(--muted)" }}>{label}</span> : null}
      <input
        {...props}
        style={{
          border: "1px solid var(--border)",
          padding: "10px 12px",
          borderRadius: 10,
          outline: "none",
          ...style,
        }}
      />
      {error ? <span style={{ fontSize: 12, color: "crimson" }}>{error}</span> : null}
    </label>
  );
}
