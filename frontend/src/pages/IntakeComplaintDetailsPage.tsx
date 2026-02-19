import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import MainLayout from "../components/layout/MainLayout";
import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";

import { getApiErrorMessage } from "../services/apiErrors";
import {
  cadetReview,
  createComplaint,
  deleteComplaint,
  getComplaint,
  officerReview,
  patchComplaint,
  resubmitComplaint,
} from "../services/intakeComplaintsService";

type BackendComplaint = Record<string, unknown> & { id?: number };

function isNumber(v: unknown): v is number {
  return typeof v === "number" && Number.isFinite(v);
}

function pickString(obj: Record<string, unknown>, key: string): string {
  const v = obj[key];
  return typeof v === "string" ? v : "";
}

export default function IntakeComplaintDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const isNew = id === "new" || !id;

  const complaintId = useMemo(() => {
    if (isNew) return null;
    const n = Number(id);
    return Number.isFinite(n) ? n : null;
  }, [id, isNew]);

  const [data, setData] = useState<BackendComplaint | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    if (!complaintId) return;
    setLoading(true);
    setError(null);
    try {
      const d = await getComplaint(complaintId);
      setData(d);
      setTitle(pickString(d as Record<string, unknown>, "title"));
      setDescription(pickString(d as Record<string, unknown>, "description"));
    } catch (e) {
      setError(getApiErrorMessage(e));
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, [complaintId]);

  const save = async () => {
    if (saving) return;

    setSaving(true);
    setError(null);

    try {
      if (isNew) {
        const created = await createComplaint({
          title: title.trim(),
          description: description.trim(),
        });

        const newId = (created as BackendComplaint).id;
        if (isNumber(newId)) {
          navigate(`/intake/complaints/${newId}`);
        } else {
          navigate("/intake/complaints");
        }
      } else if (complaintId) {
        const updated = await patchComplaint(complaintId, {
          title: title.trim(),
          description: description.trim(),
        });
        setData(updated);
      }
    } catch (e) {
      setError(getApiErrorMessage(e));
    } finally {
      setSaving(false);
    }
  };

  const doDelete = async () => {
    if (!complaintId) return;
    if (!confirm("Delete this complaint?")) return;

    setSaving(true);
    setError(null);
    try {
      await deleteComplaint(complaintId);
      navigate("/intake/complaints");
    } catch (e) {
      setError(getApiErrorMessage(e));
    } finally {
      setSaving(false);
    }
  };

  const doAction = async (fn: () => Promise<unknown>) => {
    if (saving) return;
    setSaving(true);
    setError(null);
    try {
      await fn();
      await load();
    } catch (e) {
      setError(getApiErrorMessage(e));
    } finally {
      setSaving(false);
    }
  };

  if (!isNew && complaintId === null) {
    return (
      <MainLayout title="Complaint">
        <Card title="Invalid ID">
          <Link to="/intake/complaints" style={{ fontWeight: 800 }}>
            ← Back
          </Link>
        </Card>
      </MainLayout>
    );
  }

  return (
    <MainLayout title={isNew ? "New complaint" : `Complaint #${complaintId}`}>
      <div style={{ display: "grid", gap: 14 }}>
        <Card title="Edit">
          {error ? <p style={{ margin: 0, color: "crimson", fontWeight: 800 }}>{error}</p> : null}

          {loading ? (
            <p style={{ margin: 0, color: "var(--muted)" }}>Loading...</p>
          ) : (
            <div style={{ display: "grid", gap: 12 }}>
              <Input
                label="Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Complaint title"
              />

              <Input
                label="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Description"
              />

              <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                <Button onClick={() => void save()} disabled={saving || !title.trim()}>
                  {saving ? "Saving..." : "Save"}
                </Button>

                {!isNew ? (
                  <Button variant="secondary" onClick={doDelete} disabled={saving}>
                    Delete
                  </Button>
                ) : null}

                <Link to="/intake/complaints" style={{ fontWeight: 800, alignSelf: "center" }}>
                  ← Back
                </Link>
              </div>
            </div>
          )}
        </Card>

        {!isNew && complaintId ? (
          <Card title="Workflow">
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <Button
                variant="secondary"
                onClick={() => void doAction(() => cadetReview(complaintId))}
                disabled={saving}
              >
                Cadet review
              </Button>

              <Button
                variant="secondary"
                onClick={() => void doAction(() => officerReview(complaintId))}
                disabled={saving}
              >
                Officer review
              </Button>

              <Button
                variant="secondary"
                onClick={() => void doAction(() => resubmitComplaint(complaintId))}
                disabled={saving}
              >
                Resubmit
              </Button>
            </div>

            {data ? (
              <pre
                style={{
                  marginTop: 12,
                  padding: 12,
                  borderRadius: 12,
                  border: "1px solid var(--border)",
                  background: "var(--bg-muted)",
                  overflow: "auto",
                  fontSize: 12,
                }}
              >
                {JSON.stringify(data, null, 2)}
              </pre>
            ) : null}
          </Card>
        ) : null}
      </div>
    </MainLayout>
  );
}
