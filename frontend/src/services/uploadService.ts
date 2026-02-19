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
  onProgress?.(0);

  const url = URL.createObjectURL(file);

  onProgress?.(100);

  return {
    url,
    fileName: file.name,
    size: file.size,
    mimeType: file.type || "application/octet-stream",
  };
}
