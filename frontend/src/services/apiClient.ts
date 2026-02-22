import axios, { AxiosError, type AxiosRequestConfig } from "axios";
import { clearToken, getRefreshToken, getToken, setToken } from "../features/auth/authStorage";

type RefreshResponse = { access: string };

type RetryConfig = AxiosRequestConfig & {
  _retry?: boolean;
};


const baseURL =
  import.meta.env.VITE_API_BASE_URL?.toString() || "http://127.0.0.1:8000/api";

export const apiClient = axios.create({
  baseURL,
  withCredentials: false,
});

let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refresh = getRefreshToken();
  if (!refresh) throw new Error("No refresh token");

  const { data } = await axios.post<RefreshResponse>(
    "http://127.0.0.1:8000/api/token/refresh/",
    { refresh },
    { headers: { "Content-Type": "application/json" } },
  );

  if (!data?.access) throw new Error("No access token in refresh response");

  setToken(data.access);
  return data.access;
}

apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers = config.headers ?? {};
    (config.headers as Record<string, string>).Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const status = error.response?.status;
    const originalRequest = error.config as RetryConfig | undefined;

    if (!originalRequest) return Promise.reject(error);

    const url = String(originalRequest.url ?? "");
    const isAuthRequest =
      url.includes("/auth/login/") || url.includes("/token/") || url.includes("/auth/register/");

    if (status !== 401 || originalRequest._retry || isAuthRequest) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }

      const newAccess = await refreshPromise;

      originalRequest.headers = originalRequest.headers ?? {};
      (originalRequest.headers as Record<string, string>).Authorization = `Bearer ${newAccess}`;

      return apiClient.request(originalRequest);
    } catch (e) {
      clearToken();
      return Promise.reject(e);
    }
  },
);
