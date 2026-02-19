import { useMemo, useState } from "react";

import MainLayout from "../components/layout/MainLayout";
import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";

import { trackCaseStatus, type CaseStatusResult } from "../services/caseStatusService";
import { formatCaseStatus, formatComplaintType } from "../services/casesService";
import { getApiErrorMessage } from "../services/apiErrors";

export default function CaseComplaintsStatusPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CaseStatusResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onTrack = async () => {
    const q = query.trim();
    if (!q) return;

    setLoading(true);
    setError(null);

    try {
      const data = await trackCaseStatus(q);

      if (!data) {
        setResult(null);
        setError("No case found for this tracking code.");
        return;
      }

      setResult(data);
    } catch (err) {
      setResult(null);
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const header = useMemo(() => {
    if (!result) return null;
    return `${result.caseId} • ${formatCaseStatus(result.currentStatus)}`;
  }, [result]);

  return (
    <MainLayout title="Case status">
      <div style={{ display: "grid", gap: 14 }}>
        <Card title="Track your case">
          <div
            className="no-print"
            style={{ display: "grid", gap: 12, gridTemplateColumns: "1fr auto" }}
          >
            <Input
              label="Case ID / Tracking code"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. C-1001"
            />
            <div style={{ alignSelf: "end" }}>
              <Button onClick={() => void onTrack()} disabled={loading || !query.trim()}>
                {loading ? "Tracking..." : "Track"}
              </Button>
            </div>
          </div>

          <p style={{ margin: "10px 0 0 0", color: "var(--muted)", fontSize: 13 }}>
            Use the case ID you received after submitting a complaint.
          </p>
        </Card>

        {error ? (
          <Card title="Result">
            <p style={{ margin: 0, color: "crimson", fontWeight: 700 }}>{error}</p>
          </Card>
        ) : null}

        {result ? (
          <>
            <Card title={header ?? "Result"}>
              <div style={{ display: "grid", gap: 8 }}>
                <MetaRow label="Title" value={result.title} />
                <MetaRow label="Type" value={formatComplaintType(result.complaintType)} />
                <MetaRow label="Current status" value={formatCaseStatus(result.currentStatus)} />
                <MetaRow label="Created" value={new Date(result.createdAt).toLocaleString()} />
                <MetaRow
                  label="Last update"
                  value={result.updatedAt ? new Date(result.updatedAt).toLocaleString() : "—"}
                />
              </div>
            </Card>

            <Card title="Timeline">
              <Timeline items={result.timeline} />
            </Card>
          </>
        ) : null}
      </div>
    </MainLayout>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: "flex", gap: 10 }}>
      <div style={{ width: 130, color: "var(--muted)" }}>{label}</div>
      <div style={{ fontWeight: 800 }}>{value}</div>
    </div>
  );
}

function Timeline({ items }: { items: CaseStatusResult["timeline"] }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      {items.map((it, idx) => (
        <div
          key={`${it.at}-${idx}`}
          style={{ display: "grid", gridTemplateColumns: "18px 1fr", gap: 10 }}
        >
          <div style={{ display: "grid", justifyItems: "center" }}>
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: 999,
                background: "var(--primary)",
                marginTop: 4,
              }}
            />
            {idx !== items.length - 1 ? (
              <div style={{ width: 2, flex: 1, background: "var(--border)", height: "100%" }} />
            ) : null}
          </div>

          <div
            style={{
              border: "1px solid var(--border)",
              borderRadius: 12,
              padding: 12,
              background: "white",
            }}
          >
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "baseline" }}>
              <div style={{ fontWeight: 900 }}>{it.title}</div>
              <div style={{ fontSize: 13, color: "var(--muted)" }}>
                {formatCaseStatus(it.status)}
              </div>
            </div>
            <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 4 }}>
              {new Date(it.at).toLocaleString()}
            </div>
            {it.description ? (
              <p style={{ margin: "8px 0 0 0", color: "var(--muted)" }}>{it.description}</p>
            ) : null}
          </div>
        </div>
      ))}
    </div>
  );
}
