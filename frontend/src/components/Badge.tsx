type Props = {
  text: string;
};

export default function Badge({ text }: Props) {
  return (
    <span
      style={{
        display: "inline-flex",
        width: "fit-content",
        border: "1px solid var(--border)",
        padding: "4px 10px",
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 900,
        background: "var(--bg-muted)",
      }}
    >
      {text}
    </span>
  );
}
