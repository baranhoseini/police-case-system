import { useMemo, useRef, useState } from "react";
import Button from "./Button";
import Card from "./Card";

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

export default function MediaUploader({ mediaType, maxSizeMB = 10 }: Props) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);

  const accept = useMemo(() => allowedMimeTypes(mediaType).join(","), [mediaType]);
  const maxBytes = maxSizeMB * 1024 * 1024;

  const pick = () => inputRef.current?.click();

  const onChoose = (f: File | null) => {
    setFile(null);
    if (!f) return;
    if (f.size > maxBytes) return;
    setFile(f);
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
          <Button variant="secondary" onClick={pick}>
            Choose file
          </Button>
          <Button
            onClick={() => {
              alert("Upload endpoint is not available. Please paste a URL in the URL field.");
            }}
            disabled={!file}
          >
            Upload
          </Button>
        </div>

        <div style={{ fontSize: 13, color: "var(--muted)" }}>
          Supported: {allowedMimeTypes(mediaType).join(", ")} • Max: {maxSizeMB} MB
        </div>
      </div>
    </Card>
  );
}
