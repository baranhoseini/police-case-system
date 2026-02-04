import type { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary";
};

export default function Button({ variant = "primary", style, ...props }: Props) {
  const base: React.CSSProperties = {
    border: "1px solid var(--border)",
    padding: "10px 14px",
    borderRadius: 10,
    cursor: "pointer",
    fontWeight: 600,
  };

  const variants: Record<string, React.CSSProperties> = {
    primary: { background: "var(--primary)", color: "white", borderColor: "var(--primary)" },
    secondary: { background: "white", color: "var(--primary)" },
  };

  return <button {...props} style={{ ...base, ...variants[variant], ...style }} />;
}
