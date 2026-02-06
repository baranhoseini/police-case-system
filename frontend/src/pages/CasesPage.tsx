import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import Card from "../components/Card";
import Input from "../components/Input";
import MainLayout from "../components/layout/MainLayout";
import Table, { Td, Th } from "../components/Table";
import Skeleton from "../components/Skeleton";
import EmptyState from "../components/EmptyState";

import type { CaseStatus, CaseSummary } from "../types/case";
import { formatCaseStatus, formatComplaintType, getCases } from "../services/casesService";

const STATUS_OPTIONS: Array<CaseStatus | "ALL"> = [
  "ALL",
  "DRAFT",
  "SUBMITTED",
  "UNDER_REVIEW",
  "ACTIVE",
  "CLOSED",
  "REJECTED",
];

export default function CasesPage() {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<CaseStatus | "ALL">("ALL");
  const [items, setItems] = useState<CaseSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        setLoading(true);
        const data = await getCases({ q, status });
        if (mounted) setItems(data);
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => {
      mounted = false;
    };
  }, [q, status]);

  const statusLabel = useMemo(
    () => (status === "ALL" ? "All statuses" : formatCaseStatus(status)),
    [status],
  );

  return (
    <MainLayout title="Cases">
      <div style={{ display: "grid", gap: 14 }}>
        <Card title="Search and filter">
          <div style={{ display: "grid", gap: 12, gridTemplateColumns: "1fr 240px" }}>
            <Input
              label="Search"
              placeholder="Search by ID, title, or type..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />

            <label style={{ display: "grid", gap: 6 }}>
              <span style={{ fontSize: 14, color: "var(--muted)" }}>Status</span>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as CaseStatus | "ALL")}
                style={{
                  border: "1px solid var(--border)",
                  padding: "10px 12px",
                  borderRadius: 10,
                  background: "white",
                }}
              >
                {STATUS_OPTIONS.map((s) => (
                  <option key={s} value={s}>
                    {s === "ALL" ? "All" : formatCaseStatus(s)}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </Card>

        <Card title={`Results • ${statusLabel}`}>
          {loading ? (
            <div style={{ display: "grid", gap: 10 }}>
              <Skeleton height={16} width="30%" />
              <Skeleton height={38} />
              <Skeleton height={38} />
              <Skeleton height={38} />
            </div>
          ) : items.length === 0 ? (
            <EmptyState
              title="No cases found"
              description="Try adjusting your search or status filter."
            />
          ) : (
            <Table>
              <thead>
                <tr>
                  <Th>Case ID</Th>
                  <Th>Title</Th>
                  <Th>Type</Th>
                  <Th>Status</Th>
                  <Th>Created</Th>
                </tr>
              </thead>
              <tbody>
                {items.map((c) => (
                  <tr key={c.id}>
                    <Td>
                      <Link to={`/cases/${c.id}`} style={{ fontWeight: 800 }}>
                        {c.id}
                      </Link>
                    </Td>
                    <Td>{c.title}</Td>
                    <Td>{formatComplaintType(c.complaintType)}</Td>
                    <Td>{formatCaseStatus(c.status)}</Td>
                    <Td>{new Date(c.createdAt).toLocaleDateString()}</Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card>
      </div>
    </MainLayout>
  );
}
