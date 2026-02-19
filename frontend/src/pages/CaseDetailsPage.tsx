import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import Card from "../components/Card";
import MainLayout from "../components/layout/MainLayout";
import Tabs, { type TabKey } from "../components/Tabs";
import Table, { Td, Th } from "../components/Table";

import { getCaseDetails, type CaseDetailsBundle } from "../services/caseDetailsService";
import { formatCaseStatus, formatComplaintType } from "../services/casesService";
import Breadcrumbs from "../components/Breadcrumbs";

const TAB_OVERVIEW = "overview";
const TAB_EVIDENCE = "evidence";
const TAB_SUSPECTS = "suspects";
const TAB_TIMELINE = "timeline";
const TAB_DECISIONS = "decisions";

export default function CaseDetailsPage() {
  const { caseId } = useParams();
  const [activeTab, setActiveTab] = useState<TabKey>(TAB_OVERVIEW);

  const [data, setData] = useState<CaseDetailsBundle | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        setLoading(true);
        const res = await getCaseDetails(caseId ?? "");
        if (mounted) setData(res);
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => {
      mounted = false;
    };
  }, [caseId]);

  const tabs = useMemo(
    () => [
      { key: TAB_OVERVIEW, label: "Overview" },
      { key: TAB_EVIDENCE, label: "Evidence" },
      { key: TAB_SUSPECTS, label: "Suspects" },
      { key: TAB_TIMELINE, label: "Timeline" },
      { key: TAB_DECISIONS, label: "Decisions" },
    ],
    [],
  );

  if (!caseId) {
    return (
      <MainLayout title="Case details">
        <Card title="Missing case ID">
          <p style={{ marginTop: 0, color: "var(--muted)" }}>
            No case ID was provided in the route.
          </p>
          <Link to="/cases" style={{ fontWeight: 800 }}>
            ← Back to cases
          </Link>
        </Card>
      </MainLayout>
    );
  }

  const displayId = `C-${caseId}`;

  return (
    <MainLayout title="Case details">
      <Breadcrumbs
        items={[
          { label: "Dashboard", to: "/dashboard" },
          { label: "Cases", to: "/cases" },
          { label: displayId },
        ]}
      />
      <div style={{ display: "grid", gap: 14 }}>
        <Card title={`Case: ${displayId}`}>
          {loading ? (
            <p style={{ margin: 0, color: "var(--muted)" }}>Loading case details...</p>
          ) : !data ? (
            <p style={{ margin: 0, color: "var(--muted)" }}>Case not found.</p>
          ) : (
            <CaseHeader bundle={data} />
          )}

          <div style={{ marginTop: 12 }}>
            <Link to="/cases" style={{ fontWeight: 800 }}>
              ← Back to cases
            </Link>
          </div>
        </Card>

        <Card title="Details">
          <Tabs tabs={tabs} activeKey={activeTab} onChange={setActiveTab} />
          <div style={{ marginTop: 12 }}>
            {loading ? (
              <p style={{ margin: 0, color: "var(--muted)" }}>Loading...</p>
            ) : !data ? (
              <p style={{ margin: 0, color: "var(--muted)" }}>Nothing to display.</p>
            ) : (
              <TabBody activeTab={activeTab} bundle={data} />
            )}
          </div>
        </Card>
      </div>
    </MainLayout>
  );
}

function CaseHeader({ bundle }: { bundle: CaseDetailsBundle }) {
  const c = bundle.case;

  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
        <div style={{ fontSize: 18, fontWeight: 900 }}>{c.title}</div>
        <Badge text={formatCaseStatus(c.status)} />
        <span style={{ color: "var(--muted)", fontSize: 13 }}>
          {formatComplaintType(c.complaintType)}
        </span>
      </div>

      <p style={{ margin: 0, color: "var(--muted)" }}>{c.description}</p>

      <div style={{ display: "grid", gap: 6, fontSize: 14 }}>
        <MetaRow label="Reporter" value={c.reporterName ?? "—"} />
        <MetaRow label="Contact" value={c.reporterContact ?? "—"} />
        <MetaRow label="Created" value={new Date(c.createdAt).toLocaleString()} />
        <MetaRow
          label="Last update"
          value={c.updatedAt ? new Date(c.updatedAt).toLocaleString() : "—"}
        />
      </div>
    </div>
  );
}

function TabBody({ activeTab, bundle }: { activeTab: TabKey; bundle: CaseDetailsBundle }) {
  if (activeTab === TAB_OVERVIEW) return <OverviewTab bundle={bundle} />;
  if (activeTab === TAB_EVIDENCE) return <EvidenceTab bundle={bundle} />;
  if (activeTab === TAB_SUSPECTS) return <SuspectsTab bundle={bundle} />;
  if (activeTab === TAB_TIMELINE) return <TimelineTab bundle={bundle} />;
  if (activeTab === TAB_DECISIONS) return <DecisionsTab bundle={bundle} />;
  return null;
}

function OverviewTab({ bundle }: { bundle: CaseDetailsBundle }) {
  const c = bundle.case;

  return (
    <div style={{ display: "grid", gap: 10 }}>
      <Card title="Summary">
        <div style={{ display: "grid", gap: 6 }}>
          <MetaRow label="Case ID" value={c.id} />
          <MetaRow label="Status" value={formatCaseStatus(c.status)} />
          <MetaRow label="Type" value={formatComplaintType(c.complaintType)} />
          <MetaRow label="Evidence items" value={String(c.evidenceIds.length)} />
          <MetaRow label="Suspects" value={String(c.suspectIds.length)} />
        </div>
      </Card>

      <Card title="Description">
        <p style={{ marginTop: 0, color: "var(--muted)" }}>{c.description}</p>
      </Card>
    </div>
  );
}

function EvidenceTab({ bundle }: { bundle: CaseDetailsBundle }) {
  // For now we only show IDs; Step 17 will build full Evidence module
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <p style={{ margin: 0, color: "var(--muted)" }}>
        Evidence records will be displayed here. (Full evidence UI is built in Step 17.)
      </p>

      <Table>
        <thead>
          <tr>
            <Th>Evidence ID</Th>
            <Th>Status</Th>
          </tr>
        </thead>
        <tbody>
          {bundle.case.evidenceIds.map((id) => (
            <tr key={id}>
              <Td>{id}</Td>
              <Td>Pending</Td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}

function SuspectsTab({ bundle }: { bundle: CaseDetailsBundle }) {
  // For now we only show IDs; can be expanded later
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <p style={{ margin: 0, color: "var(--muted)" }}>Suspect profiles will be displayed here.</p>

      <Table>
        <thead>
          <tr>
            <Th>Suspect ID</Th>
            <Th>Priority</Th>
          </tr>
        </thead>
        <tbody>
          {bundle.case.suspectIds.map((id) => (
            <tr key={id}>
              <Td>{id}</Td>
              <Td>Normal</Td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}

function TimelineTab({ bundle }: { bundle: CaseDetailsBundle }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      {bundle.timeline.map((t) => (
        <Card key={t.id} title={new Date(t.at).toLocaleString()}>
          <p style={{ marginTop: 0, fontWeight: 900 }}>{t.title}</p>
          {t.description ? (
            <p style={{ margin: 0, color: "var(--muted)" }}>{t.description}</p>
          ) : null}
        </Card>
      ))}
    </div>
  );
}

function DecisionsTab({ bundle }: { bundle: CaseDetailsBundle }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      {bundle.decisions.length === 0 ? (
        <p style={{ margin: 0, color: "var(--muted)" }}>No decisions yet.</p>
      ) : (
        bundle.decisions.map((d) => (
          <Card key={d.id} title={new Date(d.at).toLocaleString()}>
            <p style={{ marginTop: 0, fontWeight: 900 }}>
              {d.decision === "APPROVED"
                ? "Approved"
                : d.decision === "REJECTED"
                  ? "Rejected"
                  : "Needs more information"}
            </p>
            <p style={{ margin: 0, color: "var(--muted)" }}>
              By <strong>{d.by}</strong>
            </p>
            {d.notes ? <p style={{ marginTop: 10, color: "var(--muted)" }}>{d.notes}</p> : null}
          </Card>
        ))
      )}
    </div>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: "flex", gap: 8 }}>
      <span style={{ width: 120, color: "var(--muted)" }}>{label}</span>
      <span style={{ fontWeight: 700 }}>{value}</span>
    </div>
  );
}

function Badge({ text }: { text: string }) {
  return (
    <span
      style={{
        border: "1px solid var(--border)",
        padding: "4px 8px",
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 800,
        background: "var(--bg-muted)",
      }}
    >
      {text}
    </span>
  );
}
