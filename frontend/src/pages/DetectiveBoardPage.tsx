import { useMemo, useRef, useState } from "react";
import MainLayout from "../components/layout/MainLayout";
import Card from "../components/Card";
import Button from "../components/Button";
import Input from "../components/Input";

type NoteId = string;

type Note = {
  id: NoteId;
  title: string;
  text: string;
  x: number;
  y: number;
};

type LinkEdge = {
  id: string;
  from: NoteId;
  to: NoteId;
};

function genId(prefix: string) {
  return `${prefix}-${Math.floor(100000 + Math.random() * 900000)}`;
}

export default function DetectiveBoardPage() {
  const boardRef = useRef<HTMLDivElement | null>(null);

  const [notes, setNotes] = useState<Note[]>(() => [
    {
      id: "N-1001",
      title: "Witness statement",
      text: "Saw a dark sedan near the station around 22:15.",
      x: 80,
      y: 70,
    },
    {
      id: "N-1002",
      title: "CCTV snapshot",
      text: "Vehicle leaving the area. Plate partially visible.",
      x: 420,
      y: 120,
    },
    {
      id: "N-1003",
      title: "Suspect lead",
      text: "Possible connection to a previous theft pattern.",
      x: 220,
      y: 320,
    },
  ]);

  const [links, setLinks] = useState<LinkEdge[]>(() => [
    { id: "L-1", from: "N-1001", to: "N-1002" },
  ]);

  const [linkModeFrom, setLinkModeFrom] = useState<NoteId | null>(null);

  // Add note form
  const [newTitle, setNewTitle] = useState("");
  const [newText, setNewText] = useState("");

  const noteById = useMemo(() => {
    const map = new Map<NoteId, Note>();
    for (const n of notes) map.set(n.id, n);
    return map;
  }, [notes]);

  const addNote = () => {
    const title = newTitle.trim();
    const text = newText.trim();
    if (!title || !text) return;

    setNotes((prev) => [
      ...prev,
      { id: genId("N"), title, text, x: 120 + prev.length * 30, y: 120 + prev.length * 20 },
    ]);

    setNewTitle("");
    setNewText("");
  };

  const deleteNote = (id: NoteId) => {
    setNotes((prev) => prev.filter((n) => n.id !== id));
    setLinks((prev) => prev.filter((l) => l.from !== id && l.to !== id));
    setLinkModeFrom((cur) => (cur === id ? null : cur));
  };

  const onStartLink = (fromId: NoteId) => {
    setLinkModeFrom(fromId);
  };

  const onPickLinkTarget = (toId: NoteId) => {
    if (!linkModeFrom) return;
    if (toId === linkModeFrom) {
      setLinkModeFrom(null);
      return;
    }

    const already = links.some(
      (l) => (l.from === linkModeFrom && l.to === toId) || (l.from === toId && l.to === linkModeFrom),
    );
    if (!already) {
      setLinks((prev) => [...prev, { id: genId("L"), from: linkModeFrom, to: toId }]);
    }
    setLinkModeFrom(null);
  };

  const removeLink = (id: string) => {
    setLinks((prev) => prev.filter((l) => l.id !== id));
  };

  return (
    <MainLayout title="Detective Board">
      <div style={{ display: "grid", gap: 14 }}>
        <Card title="Controls">
          <p style={{ marginTop: 0, color: "var(--muted)" }}>
            Drag notes to reposition them. Use <strong>Link</strong> then click another note to connect.
          </p>

          <div style={{ display: "grid", gap: 12, gridTemplateColumns: "1fr 1fr auto" }}>
            <Input
              label="New note title"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. Fingerprint report"
            />
            <Input
              label="New note text"
              value={newText}
              onChange={(e) => setNewText(e.target.value)}
              placeholder="Write a short note..."
            />
            <div style={{ alignSelf: "end" }}>
              <Button onClick={addNote} disabled={!newTitle.trim() || !newText.trim()}>
                Add note
              </Button>
            </div>
          </div>

          {linkModeFrom ? (
            <div style={{ marginTop: 10, color: "crimson", fontWeight: 700 }}>
              Linking mode: select a target note to connect.
            </div>
          ) : (
            <div style={{ marginTop: 10, color: "var(--muted)", fontSize: 13 }}>
              Tip: click "Link" on a note, then click the target note.
            </div>
          )}
        </Card>

        <Card title="Board">
          <div
            ref={boardRef}
            style={{
              position: "relative",
              height: 560,
              border: "1px solid var(--border)",
              borderRadius: 14,
              background: "white",
              overflow: "hidden",
            }}
          >
            {/* Lines layer */}
            <svg
              width="100%"
              height="100%"
              style={{
                position: "absolute",
                inset: 0,
                pointerEvents: "none",
              }}
            >
              {links.map((l) => {
                const a = noteById.get(l.from);
                const b = noteById.get(l.to);
                if (!a || !b) return null;

                const ax = a.x + 150; // approximate center of note card
                const ay = a.y + 46;
                const bx = b.x + 150;
                const by = b.y + 46;

                return (
                  <g key={l.id}>
                    <line x1={ax} y1={ay} x2={bx} y2={by} stroke="#b91c1c" strokeWidth="3" />
                  </g>
                );
              })}
            </svg>

            {/* Notes */}
            {notes.map((n) => (
              <NoteCard
                key={n.id}
                note={n}
                linkingFrom={linkModeFrom}
                onMove={(id, x, y) =>
                  setNotes((prev) => prev.map((p) => (p.id === id ? { ...p, x, y } : p)))
                }
                onDelete={() => deleteNote(n.id)}
                onStartLink={() => onStartLink(n.id)}
                onPickAsTarget={() => onPickLinkTarget(n.id)}
              />
            ))}
          </div>
        </Card>

        <Card title="Links">
          {links.length === 0 ? (
            <p style={{ margin: 0, color: "var(--muted)" }}>No links yet.</p>
          ) : (
            <div style={{ display: "grid", gap: 8 }}>
              {links.map((l) => (
                <div
                  key={l.id}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 10,
                    padding: "10px 12px",
                    border: "1px solid var(--border)",
                    borderRadius: 12,
                    background: "var(--bg-muted)",
                  }}
                >
                  <div style={{ fontWeight: 800 }}>
                    {noteById.get(l.from)?.title ?? l.from} → {noteById.get(l.to)?.title ?? l.to}
                  </div>
                  <button
                    type="button"
                    onClick={() => removeLink(l.id)}
                    style={{
                      border: "1px solid var(--border)",
                      padding: "6px 10px",
                      borderRadius: 10,
                      cursor: "pointer",
                      background: "white",
                      fontWeight: 700,
                    }}
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </MainLayout>
  );
}

function NoteCard({
  note,
  linkingFrom,
  onMove,
  onDelete,
  onStartLink,
  onPickAsTarget,
}: {
  note: Note;
  linkingFrom: NoteId | null;
  onMove: (id: NoteId, x: number, y: number) => void;
  onDelete: () => void;
  onStartLink: () => void;
  onPickAsTarget: () => void;
}) {
  const dragging = useRef(false);
  const offset = useRef({ dx: 0, dy: 0 });

  const isLinkingTargetMode = Boolean(linkingFrom && linkingFrom !== note.id);

  const onPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    // If we're in linking mode, clicking the note should select it as target (not drag)
    if (isLinkingTargetMode) {
      onPickAsTarget();
      return;
    }

    dragging.current = true;
    const rect = e.currentTarget.getBoundingClientRect();
    offset.current = { dx: e.clientX - rect.left, dy: e.clientY - rect.top };
    (e.currentTarget as HTMLDivElement).setPointerCapture(e.pointerId);
  };

  const onPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!dragging.current) return;

    const board = (e.currentTarget.parentElement as HTMLDivElement).getBoundingClientRect();
    const x = e.clientX - board.left - offset.current.dx;
    const y = e.clientY - board.top - offset.current.dy;

    // Keep inside board (simple clamp)
    const clampedX = Math.max(0, Math.min(x, board.width - 300));
    const clampedY = Math.max(0, Math.min(y, board.height - 120));

    onMove(note.id, clampedX, clampedY);
  };

  const onPointerUp = () => {
    dragging.current = false;
  };

  const borderColor = linkingFrom === note.id ? "#b91c1c" : "var(--border)";

  return (
    <div
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      role="button"
      tabIndex={0}
      style={{
        position: "absolute",
        left: note.x,
        top: note.y,
        width: 300,
        border: `2px solid ${borderColor}`,
        borderRadius: 14,
        background: "white",
        boxShadow: "0 6px 18px rgba(0,0,0,0.08)",
        padding: 12,
        cursor: isLinkingTargetMode ? "crosshair" : "grab",
        userSelect: "none",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
        <div style={{ fontWeight: 900 }}>{note.title}</div>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          style={{
            border: "1px solid var(--border)",
            padding: "4px 8px",
            borderRadius: 10,
            cursor: "pointer",
            background: "white",
            fontWeight: 800,
          }}
        >
          Delete
        </button>
      </div>

      <p style={{ margin: "8px 0 10px 0", color: "var(--muted)", fontSize: 13 }}>{note.text}</p>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onStartLink();
          }}
          style={{
            border: "1px solid var(--border)",
            padding: "6px 10px",
            borderRadius: 10,
            cursor: "pointer",
            background: "white",
            fontWeight: 800,
          }}
        >
          Link
        </button>

        {isLinkingTargetMode ? (
          <span style={{ alignSelf: "center", color: "#b91c1c", fontWeight: 800, fontSize: 12 }}>
            Click to connect
          </span>
        ) : null}
      </div>
    </div>
  );
}
