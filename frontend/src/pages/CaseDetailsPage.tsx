import { Link, useParams } from "react-router-dom";
import Card from "../components/Card";
import MainLayout from "../components/layout/MainLayout";

export default function CaseDetailsPage() {
  const { caseId } = useParams();

  return (
    <MainLayout title="Case details">
      <Card title={`Case: ${caseId ?? ""}`}>
        <p style={{ marginTop: 0, color: "var(--muted)" }}>
          This page will show case details, evidence, suspects, timeline, and decisions.
        </p>

        <Link to="/cases" style={{ fontWeight: 800 }}>
          ← Back to cases
        </Link>
      </Card>
    </MainLayout>
  );
}
