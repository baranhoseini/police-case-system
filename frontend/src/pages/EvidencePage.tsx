import { useEffect, useMemo, useState } from "react";
import MediaUploader from "../components/MediaUploader";

import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";
import MainLayout from "../components/layout/MainLayout";
import Table, { Td, Th } from "../components/Table";

import type { Evidence } from "../types/evidence";
import {
  addEvidence,
  formatEvidenceKind,
  formatEvidenceStatus,
  listEvidence,
  setEvidenceStatus,
} from "../services/evidenceService";
import { getApiErrorMessage } from "../services/apiErrors";

type EvidenceKind = Evidence["kind"];

export default function EvidencePage() {
  const [caseId, setCaseId] = useState<string>("");
  const [items, setItems] = useState<Evidence[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listEvidence({ caseId: caseId.trim() || undefined });
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  return (
    <MainLayout title="Evidence">
      <div style={{ display: "grid", gap: 14 }}>
        <Card title="Filter">
          <div style={{ display: "grid", gap: 12, gridTemplateColumns: "1fr 220px" }}>
            <Input
              label="Case ID"
              value={caseId}
              onChange={(e) => setCaseId(e.target.value)}
              placeholder='e.g. C-1 (leave empty for all)'
            />
            <div style={{ alignSelf: "end" }}>
              <Button variant="secondary" onClick={() => void refresh()}>
                Refresh
              </Button>
            </div>
          </div>
        </Card>

        <AddEvidenceCard defaultCaseId={caseId} onAdded={() => void refresh()} />

        <Card title="Evidence list">
          {error ? <p style={{ margin: 0, color: "crimson", fontWeight: 800 }}>{error}</p> : null}

          {loading ? (
            <p style={{ margin: 0, color: "var(--muted)" }}>Loading evidence...</p>
          ) : items.length === 0 ? (
            <p style={{ margin: 0, color: "var(--muted)" }}>No evidence found.</p>
          ) : (
            <EvidenceTable items={items} onChanged={() => void refresh()} />
          )}
        </Card>
      </div>
    </MainLayout>
  );
}

function EvidenceTable({ items, onChanged }: { items: Evidence[]; onChanged: () => void }) {
  const [busyId, setBusyId] = useState<string | null>(null);

  return (
    <Table>
      <thead>
        <tr>
          <Th>ID</Th>
          <Th>Case</Th>
          <Th>Kind</Th>
          <Th>Title</Th>
          <Th>Status</Th>
          <Th>Created</Th>
          <Th>Actions</Th>
        </tr>
      </thead>
      <tbody>
        {items.map((e) => (
          <tr key={e.id}>
            <Td>{e.id}</Td>
            <Td>{e.caseId}</Td>
            <Td>{formatEvidenceKind(e.kind)}</Td>
            <Td>{e.title}</Td>
            <Td>{formatEvidenceStatus(e.status)}</Td>
            <Td>{new Date(e.createdAt).toLocaleString()}</Td>
            <Td>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <button
                  type="button"
                  disabled={busyId === e.id}
                  onClick={async () => {
                    setBusyId(e.id);
                    try {
                      await setEvidenceStatus(e.id, "VERIFIED");
                      onChanged();
                    } catch (err) {
                      alert(getApiErrorMessage(err));
                    } finally {
                      setBusyId(null);
                    }
                  }}
                  style={smallActionStyle()}
                >
                  Verify
                </button>
                <button
                  type="button"
                  disabled={busyId === e.id}
                  onClick={async () => {
                    setBusyId(e.id);
                    try {
                      await setEvidenceStatus(e.id, "REJECTED");
                      onChanged();
                    } catch (err) {
                      alert(getApiErrorMessage(err));
                    } finally {
                      setBusyId(null);
                    }
                  }}
                  style={smallActionStyle()}
                >
                  Reject
                </button>
              </div>
            </Td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
}

function AddEvidenceCard({ defaultCaseId, onAdded }: { defaultCaseId: string; onAdded: () => void }) {
  const [kind, setKind] = useState<EvidenceKind>("IDENTITY");

  const [caseId, setCaseId] = useState(defaultCaseId || "");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const [kvKey, setKvKey] = useState("");
  const [kvValue, setKvValue] = useState("");
  const [identityFields, setIdentityFields] = useState<Record<string, string>>({});

  const [plateNumber, setPlateNumber] = useState("");
  const [vin, setVin] = useState("");
  const [model, setModel] = useState("");
  const [color, setColor] = useState("");

  const [sampleType, setSampleType] = useState("");
  const [labNotes, setLabNotes] = useState("");

  const [mediaType, setMediaType] = useState<"IMAGE" | "VIDEO" | "AUDIO">("IMAGE");
  const [url, setUrl] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    setCaseId(defaultCaseId || "");
  }, [defaultCaseId]);

  const canSubmit = useMemo(() => {
    if (!caseId.trim()) return false;
    if (!title.trim()) return false;

    if (kind === "IDENTITY") return Object.keys(identityFields).length > 0;
    if (kind === "VEHICLE") return Boolean(plateNumber.trim() || vin.trim() || model.trim() || color.trim());
    if (kind === "MEDICAL") return Boolean(sampleType.trim() || labNotes.trim());
    if (kind === "MEDIA") return Boolean(url.trim());
    return false;
  }, [caseId, title, kind, identityFields, plateNumber, vin, model, color, sampleType, labNotes, url]);

  const reset = () => {
    setTitle("");
    setDescription("");
    setIdentityFields({});
    setKvKey("");
    setKvValue("");
    setPlateNumber("");
    setVin("");
    setModel("");
    setColor("");
    setSampleType("");
    setLabNotes("");
    setMediaType("IMAGE");
    setUrl("");
    setSubmitError(null);
  };

  const submit = async () => {
    if (!canSubmit || submitting) return;

    setSubmitting(true);
    setSubmitError(null);

    try {
      if (kind === "IDENTITY") {
        await addEvidence({
          kind: "IDENTITY",
          caseId: caseId.trim(),
          title: title.trim(),
          description: description.trim() || undefined,
          fields: identityFields,
        });
      }

      if (kind === "VEHICLE") {
        await addEvidence({
          kind: "VEHICLE",
          caseId: caseId.trim(),
          title: title.trim(),
          description: description.trim() || undefined,
          plateNumber: plateNumber.trim() || undefined,
          vin: vin.trim() || undefined,
          model: model.trim() || undefined,
          color: color.trim() || undefined,
        });
      }

      if (kind === "MEDICAL") {
        await addEvidence({
          kind: "MEDICAL",
          caseId: caseId.trim(),
          title: title.trim(),
          description: description.trim() || undefined,
          sampleType: sampleType.trim() || undefined,
          labNotes: labNotes.trim() || undefined,
        });
      }

      if (kind === "MEDIA") {
        await addEvidence({
          kind: "MEDIA",
          caseId: caseId.trim(),
          title: title.trim(),
          description: description.trim() || undefined,
          mediaType,
          url: url.trim(),
        });
      }

      reset();
      onAdded();
    } catch (e) {
      setSubmitError(getApiErrorMessage(e));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card title="Add evidence">
      <div style={{ display: "grid", gap: 12 }}>
        {submitError ? <div style={{ color: "crimson", fontSize: 13, fontWeight: 800 }}>{submitError}</div> : null}

        <div style={{ display: "grid", gridTemplateColumns: "1fr 260px", gap: 12 }}>
          <Input
            label="Case ID"
            value={caseId}
            onChange={(e) => setCaseId(e.target.value)}
            placeholder="C-1"
          />
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ fontSize: 14, color: "var(--muted)" }}>Type</span>
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value as EvidenceKind)}
              style={{
                border: "1px solid var(--border)",
                padding: "10px 12px",
                borderRadius: 10,
                background: "white",
              }}
            >
              <option value="IDENTITY">Identity</option>
              <option value="VEHICLE">Vehicle</option>
              <option value="MEDICAL">Medical</option>
              <option value="MEDIA">Media</option>
            </select>
          </label>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Evidence title" />
          <Input
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional description"
          />
        </div>

        {kind === "IDENTITY" ? (
          <Card title="Identity fields (key-value)">
            <div style={{ display: "grid", gap: 10, gridTemplateColumns: "1fr 1fr auto" }}>
              <Input label="Key" value={kvKey} onChange={(e) => setKvKey(e.target.value)} placeholder="e.g. Passport" />
              <Input label="Value" value={kvValue} onChange={(e) => setKvValue(e.target.value)} placeholder="e.g. 123456789" />
              <div style={{ alignSelf: "end" }}>
                <Button
                  variant="secondary"
                  onClick={() => {
                    const k = kvKey.trim();
                    const v = kvValue.trim();
                    if (!k || !v) return;
                    setIdentityFields((prev) => ({ ...prev, [k]: v }));
                    setKvKey("");
                    setKvValue("");
                  }}
                >
                  Add
                </Button>
              </div>
            </div>

            {Object.keys(identityFields).length === 0 ? (
              <p style={{ margin: 0, color: "var(--muted)" }}>Add at least one key-value pair.</p>
            ) : (
              <ul style={{ margin: 0, paddingLeft: 18 }}>
                {Object.entries(identityFields).map(([k, v]) => (
                  <li key={k}>
                    <strong>{k}:</strong> {v}{" "}
                    <button
                      type="button"
                      onClick={() =>
                        setIdentityFields((prev) => {
                          const next = { ...prev };
                          delete next[k];
                          return next;
                        })
                      }
                      style={{ marginLeft: 8, ...smallActionStyle() }}
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        ) : null}

        {kind === "VEHICLE" ? (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <Input label="Plate number" value={plateNumber} onChange={(e) => setPlateNumber(e.target.value)} placeholder="ABC-1234" />
            <Input label="VIN" value={vin} onChange={(e) => setVin(e.target.value)} placeholder="Optional" />
            <Input label="Model" value={model} onChange={(e) => setModel(e.target.value)} placeholder="Optional" />
            <Input label="Color" value={color} onChange={(e) => setColor(e.target.value)} placeholder="Optional" />
          </div>
        ) : null}

        {kind === "MEDICAL" ? (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <Input label="Sample type" value={sampleType} onChange={(e) => setSampleType(e.target.value)} placeholder="e.g. Blood" />
            <Input label="Lab notes" value={labNotes} onChange={(e) => setLabNotes(e.target.value)} placeholder="Optional" />
          </div>
        ) : null}

        {kind === "MEDIA" ? (
          <div style={{ display: "grid", gap: 12 }}>
            <div style={{ display: "grid", gap: 12, gridTemplateColumns: "220px 1fr" }}>
              <label style={{ display: "grid", gap: 6 }}>
                <span style={{ fontSize: 14, color: "var(--muted)" }}>Media type</span>
                <select
                  value={mediaType}
                  onChange={(e) => setMediaType(e.target.value as "IMAGE" | "VIDEO" | "AUDIO")}
                  style={{
                    border: "1px solid var(--border)",
                    padding: "10px 12px",
                    borderRadius: 10,
                    background: "white",
                  }}
                >
                  <option value="IMAGE">Image</option>
                  <option value="VIDEO">Video</option>
                  <option value="AUDIO">Audio</option>
                </select>
              </label>

              <Input
                label="URL"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Upload a file or paste a URL..."
              />
            </div>

            <MediaUploader
              mediaType={mediaType}
              maxSizeMB={10}
              onUploaded={(res) => {
                if (res.url) setUrl(res.url);
              }}

            />
          </div>
        ) : null}

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Button disabled={!canSubmit || submitting} onClick={() => void submit()}>
            {submitting ? "Adding..." : "Add evidence"}
          </Button>
          <Button variant="secondary" onClick={reset} disabled={submitting}>
            Reset
          </Button>

          {!canSubmit ? (
            <span style={{ alignSelf: "center", color: "var(--muted)", fontSize: 13 }}>
              Fill required fields before submitting.
            </span>
          ) : null}
        </div>
      </div>
    </Card>
  );
}

function smallActionStyle(): React.CSSProperties {
  return {
    border: "1px solid var(--border)",
    padding: "6px 8px",
    borderRadius: 10,
    cursor: "pointer",
    background: "white",
    fontWeight: 700,
  };
}
