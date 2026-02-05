import { useMemo, useRef, useState } from "react";
import Button from "./Button";
import Card from "./Card";
import { uploadMediaFile } from "../services/uploadService";

type MediaKind = "IMAGE" | "VIDEO" | "AUDIO";

type Props = {
  mediaType: MediaKind;
  maxSizeMB?: number;
  onUploaded: (result: { url: string; fileName: string; mimeType: string; size: number }) => void;
};

function allowedMimeTypes(mediaType: MediaKind): string[] {
  if (mediaType === "IMAGE") return ["image/png", "image/jpeg", "image/webp", "image/gif"];
  if (mediaType === "VIDEO") return ["video/mp4", "video/webm", "video/quicktime"];
  return ["audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4"];
}

export default function MediaUploader({ mediaType, maxSizeMB = 10, onUploaded }: Props) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [uploading, setUploading] = useState(false);

  const accept = useMemo(() => allowedMimeTypes(mediaType).join(","), [mediaType]);
  const maxBytes = maxSizeMB * 1024 * 1024;

  const pick = () => inputRef.current?.click();

  const validate = (f: File): string | null => {
    const okTypes = allowedMimeTypes(mediaType);
    if (f.type && !okTypes.includes(f.type)) {
      return `Unsupported file type. Please upload a valid ${mediaType.toLowerCase()} file.`;
    }
    if (f.size > maxBytes) {
      return `File is too large. Max size is ${maxSizeMB} MB.`;
    }
    return null;
  };

  const onChoose = (f: File | null) => {
    setError(null);
    setProgress(0);
    setFile(null);

    if (!f) return;
    const err = validate(f);
    if (err) {
      setError(err);
      return;
    }
    setFile(f);
  };

  const doUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setProgress(0);

    try {
      const res = await uploadMediaFile(file, setProgress);
      onUploaded(res);
    } catch {
      setError("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card title="Upload media file">
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: "none" }}
        onChange={(e) => onChoose(e.target.files?.[0] ?? null)}
      />

      <div style={{ display: "grid", gap: 10 }}>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Button variant="secondary" onClick={pick} disabled={uploading}>
            Choose file
          </Button>
          <Button onClick={() => void doUpload()} disabled={!file || uploading}>
            {uploading ? "Uploading..." : "Upload"}
          </Button>
        </div>

        {file ? (
          <div style={{ fontSize: 13, color: "var(--muted)" }}>
            Selected: <strong>{file.name}</strong> ({Math.ceil(file.size / 1024)} KB)
          </div>
        ) : (
          <div style={{ fontSize: 13, color: "var(--muted)" }}>
            Supported: {allowedMimeTypes(mediaType).join(", ")} • Max: {maxSizeMB} MB
          </div>
        )}

        {uploading ? (
          <div style={{ display: "grid", gap: 6 }}>
            <div style={{ fontSize: 13, color: "var(--muted)" }}>Progress: {progress}%</div>
            <div
              style={{
                height: 10,
                borderRadius: 999,
                border: "1px solid var(--border)",
                overflow: "hidden",
                background: "white",
              }}
            >
              <div style={{ width: `${progress}%`, height: "100%", background: "var(--primary)" }} />
            </div>
          </div>
        ) : null}

        {error ? <div style={{ color: "crimson", fontSize: 13 }}>{error}</div> : null}
      </div>
    </Card>
  );
}
