import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import MainLayout from "../components/layout/MainLayout";
import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";
import Table, { Td, Th } from "../components/Table";
import Skeleton from "../components/Skeleton";
import EmptyState from "../components/EmptyState";

import { getApiErrorMessage } from "../services/apiErrors";
import {
  listCadetInbox,
  listComplaints,
  listOfficerInbox,
  type ComplaintItem,
} from "../services/intakeComplaintsService";

type Mode = "ALL" | "CADET_INBOX" | "OFFICER_INBOX";

export default function IntakeComplaintsPage() {
  const [mode, setMode] = useState<Mode>("ALL");
  const [q, setQ] = useState("");
  const [items, setItems] = useState<ComplaintItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      const data =
        mode === "CADET_INBOX"
          ? await listCadetInbox()
          : mode === "OFFICER_INBOX"
            ? await listOfficerInbox()
            : await listComplaints();

      setItems(data);
    } catch (e) {
      setError(getApiErrorMessage(e));
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, [mode]);

  const filtered = useMemo(() => {
    const query = q.trim().toLowerCase();
    if (!query) return items;

    return items.filter((x) => {
      const title = (x.title ?? "").toLowerCase();
      const id = String(x.id);
      const status = (x.status ?? "").toLowerCase();
      return title.includes(query) || id.includes(query) || status.includes(query);
    });
  }, [items, q]);

  return (
    <MainLayout title="Intake • Complaints">
      <div style={{ display: "grid", gap: 14 }}>
        <Card title="View">
          <div style={{ display: "grid", gap: 12, gridTemplateColumns: "1fr 240px 220px" }}>
            <Input
              label="Search"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search by title, id, or status..."
            />

            <label style={{ display: "grid", gap: 6 }}>
              <span style={{ fontSize: 14, color: "var(--muted)" }}>List</span>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value as Mode)}
                style={{
                  border: "1px solid var(--border)",
                  padding: "10px 12px",
                  borderRadius: 10,
                  background: "white",
                }}
              >
                <option value="ALL">All complaints</option>
                <option value="CADET_INBOX">Cadet inbox</option>
                <option value="OFFICER_INBOX">Officer inbox</option>
              </select>
            </label>

            <div style={{ alignSelf: "end", display: "flex", gap: 10, justifyContent: "flex-end" }}>
              <Link to="/intake/complaints/new">
                <Button>Create</Button>
              </Link>
              <Button variant="secondary" onClick={() => void refresh()}>
                Refresh
              </Button>
            </div>
          </div>
        </Card>

        <Card title="Results">
          {error ? <p style={{ margin: 0, color: "crimson", fontWeight: 800 }}>{error}</p> : null}

          {loading ? (
            <div style={{ display: "grid", gap: 10 }}>
              <Skeleton height={16} width="30%" />
              <Skeleton height={38} />
              <Skeleton height={38} />
              <Skeleton height={38} />
            </div>
          ) : filtered.length === 0 ? (
            <EmptyState title="No complaints found" description="Try another search or list." />
          ) : (
            <Table>
              <thead>
                <tr>
                  <Th>ID</Th>
                  <Th>Title</Th>
                  <Th>Status</Th>
                  <Th>Created</Th>
                  <Th>Updated</Th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((x) => (
                  <tr key={x.id}>
                    <Td>
                      <Link to={`/intake/complaints/${x.id}`} style={{ fontWeight: 800 }}>
                        {x.id}
                      </Link>
                    </Td>
                    <Td>{x.title}</Td>
                    <Td>{String(x.status)}</Td>
                    <Td>{new Date(x.createdAt).toLocaleString()}</Td>
                    <Td>{x.updatedAt ? new Date(x.updatedAt).toLocaleString() : "—"}</Td>
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
