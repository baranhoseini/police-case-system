type Props = {
  height?: number;
  width?: string | number;
  radius?: number;
};

export default function Skeleton({ height = 14, width = "100%", radius = 10 }: Props) {
  return (
    <div
      aria-hidden="true"
      style={{
        height,
        width,
        borderRadius: radius,
        background: "var(--bg-muted)",
        border: "1px solid var(--border)",
      }}
    />
  );
}
