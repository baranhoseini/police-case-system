import axios from "axios";
import { getToken, clearToken } from "../features/auth/authStorage";

// Later you can move this to .env (VITE_API_BASE_URL)
const BASE_URL = "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ✅ Attach token to every request
apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ✅ Handle common errors (401/403/500...)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;

    // If token is invalid/expired
    if (status === 401) {
      clearToken();
      // We do NOT navigate here because apiClient is not a React file.
      // The UI layer (pages) will handle redirect if needed.
    }

    return Promise.reject(error);
  },
);
