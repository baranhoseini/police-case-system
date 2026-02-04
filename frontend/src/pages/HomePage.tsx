import Button from "../components/Button";
import Card from "../components/Card";

export default function HomePage() {
  return (
    <div className="container">
      <h1 style={{ marginTop: 0 }}>Home</h1>

      <Card title="Quick check">
        <p style={{ marginTop: 0, color: "var(--muted)" }}>Base UI components are working.</p>
        <div style={{ display: "flex", gap: 10 }}>
          <Button>Primary action</Button>
          <Button variant="secondary">Secondary action</Button>
        </div>
      </Card>
    </div>
  );
}
