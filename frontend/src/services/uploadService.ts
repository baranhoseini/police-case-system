export type UploadResult = {
  url: string;
  fileName: string;
  size: number;
  mimeType: string;
};

export async function uploadMediaFile(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<UploadResult> {
  // Fake upload progress
  let p = 0;
  onProgress?.(p);

  while (p < 100) {
    await new Promise((r) => setTimeout(r, 60));
    p = Math.min(100, p + Math.floor(6 + Math.random() * 12));
    onProgress?.(p);
  }

  // Fake URL (later: backend will return a real URL)
  return {
    url: `https://example.com/uploads/${encodeURIComponent(file.name)}?t=${Date.now()}`,
    fileName: file.name,
    size: file.size,
    mimeType: file.type || "application/octet-stream",
  };
}
