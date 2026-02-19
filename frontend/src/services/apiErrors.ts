import axios from "axios";

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null;
}

function pickString(v: unknown, key: string): string | null {
  if (!isRecord(v)) return null;
  const x = v[key];
  return typeof x === "string" ? x : null;
}

export function getApiErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const status = err.response?.status;
    const data: unknown = err.response?.data;

    let msg: string | null = null;

    if (isRecord(data)) {
      msg =
        pickString(data, "message") ||
        pickString(data, "detail") ||
        pickString(data, "error") ||
        null;

      const errorObj = data["error"];
      if (!msg && isRecord(errorObj)) {
        msg = pickString(errorObj, "message") || pickString(errorObj, "code") || null;

        const detailsObj = errorObj["details"];
        if (!msg && isRecord(detailsObj)) {
          msg = pickString(detailsObj, "detail") || pickString(detailsObj, "message") || null;
        }
      }
    } else if (typeof data === "string") {
      msg = data;
    }

    if (msg) return msg;

    if (status === 400) return "Bad request. Please check your input.";
    if (status === 401) return "Your session has expired. Please sign in again.";
    if (status === 403) return "You do not have permission to perform this action.";
    if (status === 404) return "Requested resource was not found.";
    if (status && status >= 500) return "Server error. Please try again later.";

    if (err.code === "ECONNABORTED") return "Request timed out. Please try again.";
    return "Network error. Please check your connection.";
  }

  return "Unexpected error. Please try again.";
}
