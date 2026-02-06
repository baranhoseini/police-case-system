import { Link } from "react-router-dom";
import MainLayout from "../components/layout/MainLayout";
import Card from "../components/Card";
import Button from "../components/Button";

export default function NotFoundPage() {
  return (
    <MainLayout title="Page not found">
      <Card title="404">
        <p style={{ marginTop: 0, color: "var(--muted)" }}>
          The page you are looking for does not exist or has been moved.
        </p>

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Link to="/">
            <Button>Go to home</Button>
          </Link>
          <Link to="/dashboard">
            <Button variant="secondary">Go to dashboard</Button>
          </Link>
        </div>
      </Card>
    </MainLayout>
  );
}
