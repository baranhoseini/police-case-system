import axios from "axios";
import { getToken, clearToken } from "../features/auth/authStorage";


export const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  headers: { "Content-Type": "application/json" },
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
