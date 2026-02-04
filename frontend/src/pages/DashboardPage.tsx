import Card from "../components/Card";
import MainLayout from "../components/layout/MainLayout";

export default function DashboardPage() {
  return (
    <MainLayout title="Dashboard">
      <Card title="Modules">
        <p style={{ marginTop: 0, color: "var(--muted)" }}>
          This dashboard will be modular and role-based.
        </p>
      </Card>
    </MainLayout>
  );
}
