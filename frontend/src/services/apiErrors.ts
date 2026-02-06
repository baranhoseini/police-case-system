import axios from "axios";

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null;
}

export function getApiErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const status = err.response?.status;
    const data: unknown = err.response?.data;

    const msg =
      isRecord(data) && typeof data.message === "string"
        ? data.message
        : isRecord(data) && typeof data.detail === "string"
          ? data.detail
          : typeof data === "string"
            ? data
            : null;

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
