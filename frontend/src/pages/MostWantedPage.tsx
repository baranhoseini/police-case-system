import { useEffect, useMemo, useState } from "react";

import MainLayout from "../components/layout/MainLayout";
import Card from "../components/Card";
import Input from "../components/Input";
import Table, { Td, Th } from "../components/Table";

import type { MostWantedItem, MostWantedLevel } from "../types/mostWanted";
import { formatMostWantedLevel, listMostWanted } from "../services/mostWantedService";

const LEVELS: Array<MostWantedLevel | "ALL"> = ["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"];

export default function MostWantedPage() {
  const [items, setItems] = useState<MostWantedItem[]>([]);
  const [loading, setLoading] = useState(true);

  const [q, setQ] = useState("");
  const [level, setLevel] = useState<MostWantedLevel | "ALL">("ALL");
  const [selected, setSelected] = useState<MostWantedItem | null>(null);

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        setLoading(true);
        const data = await listMostWanted();
        if (mounted) setItems(data);
        if (mounted) setSelected(data[0] ?? null);
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => {
      mounted = false;
    };
  }, []);

  const filtered = useMemo(() => {
    const query = q.trim().toLowerCase();
    return items.filter((x) => {
      const matchesLevel = level === "ALL" ? true : x.level === level;
      const matchesQuery =
        !query ||
        x.fullName.toLowerCase().includes(query) ||
        x.reason.toLowerCase().includes(query) ||
        (x.lastSeenLocation ?? "").toLowerCase().includes(query) ||
        x.id.toLowerCase().includes(query);

      return matchesLevel && matchesQuery;
    });
  }, [items, q, level]);

  useEffect(() => {
    // keep selection valid after filters
    if (selected && filtered.some((x) => x.id === selected.id)) return;
    setSelected(filtered[0] ?? null);
  }, [filtered, selected]);

  return (
    <MainLayout title="Most Wanted">
      <div style={{ display: "grid", gap: 14, gridTemplateColumns: "1.4fr 1fr" }}>
        <Card title="Search and filter">
          <div style={{ display: "grid", gap: 12 }}>
            <Input
              label="Search"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search by name, reason, location, or ID..."
            />

            <label style={{ display: "grid", gap: 6 }}>
              <span style={{ fontSize: 14, color: "var(--muted)" }}>Threat level</span>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value as MostWantedLevel | "ALL")}
                style={{
                  border: "1px solid var(--border)",
                  padding: "10px 12px",
                  borderRadius: 10,
                  background: "white",
                }}
              >
                {LEVELS.map((lv) => (
                  <option key={lv} value={lv}>
                    {lv === "ALL" ? "All" : formatMostWantedLevel(lv)}
                  </option>
                ))}
              </select>
            </label>

            <div style={{ fontSize: 13, color: "var(--muted)" }}>
              {loading ? "Loading..." : `${filtered.length} result(s)`}
            </div>
          </div>
        </Card>

        <Card title="Details">
          {loading ? (
            <p style={{ margin: 0, color: "var(--muted)" }}>Loading details...</p>
          ) : !selected ? (
            <p style={{ margin: 0, color: "var(--muted)" }}>Select a person to view details.</p>
          ) : (
            <MostWantedDetails item={selected} />
          )}
        </Card>

        <div style={{ gridColumn: "1 / -1" }}>
          <Card title="List">
            {loading ? (
              <p style={{ margin: 0, color: "var(--muted)" }}>Loading list...</p>
            ) : filtered.length === 0 ? (
              <p style={{ margin: 0, color: "var(--muted)" }}>No results found.</p>
            ) : (
              <Table>
                <thead>
                  <tr>
                    <Th>ID</Th>
                    <Th>Name</Th>
                    <Th>Level</Th>
                    <Th>Reward</Th>
                    <Th>Last seen</Th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((x) => (
                    <tr
                      key={x.id}
                      onClick={() => setSelected(x)}
                      style={{
                        cursor: "pointer",
                        background: selected?.id === x.id ? "var(--bg-muted)" : "transparent",
                      }}
                    >
                      <Td>{x.id}</Td>
                      <Td>
                        <strong>{x.fullName}</strong>
                      </Td>
                      <Td>{formatMostWantedLevel(x.level)}</Td>
                      <Td>€ {x.rewardAmount.toLocaleString()}</Td>
                      <Td>{x.lastSeenLocation ?? "—"}</Td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}

function MostWantedDetails({ item }: { item: MostWantedItem }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div style={{ fontSize: 18, fontWeight: 900 }}>{item.fullName}</div>
      <Badge text={formatMostWantedLevel(item.level)} />
      <p style={{ margin: 0, color: "var(--muted)" }}>{item.reason}</p>

      <div style={{ display: "grid", gap: 6, fontSize: 14 }}>
        <MetaRow label="Reward" value={`€ ${item.rewardAmount.toLocaleString()}`} />
        <MetaRow label="Last seen" value={item.lastSeenLocation ?? "—"} />
        <MetaRow label="Listed since" value={new Date(item.createdAt).toLocaleString()} />
      </div>

      <p style={{ margin: 0, color: "var(--muted)", fontSize: 13 }}>
        If you have reliable information, contact the authorities immediately.
      </p>
    </div>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: "flex", gap: 8 }}>
      <span style={{ width: 110, color: "var(--muted)" }}>{label}</span>
      <span style={{ fontWeight: 800 }}>{value}</span>
    </div>
  );
}

function Badge({ text }: { text: string }) {
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
