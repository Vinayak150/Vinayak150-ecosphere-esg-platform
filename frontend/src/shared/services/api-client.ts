import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

import type { ApiErrorResponse, ApiSuccessResponse } from "@/shared/types/api";
import type { TokenResponse } from "@/modules/auth/types/auth.types";

import {
  API_BASE_URL,
  clearAuthTokens,
  getAccessToken,
  getRefreshToken,
  setAuthTokens,
} from "./token.service";

export class ApiClientError extends Error {
  code: string;
  status: number;
  details: unknown;

  constructor(message: string, code: string, status: number, details: unknown = null) {
    super(message);
    this.name = "ApiClientError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

let isRefreshing = false;
let refreshQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

function processRefreshQueue(error: unknown, token: string | null = null): void {
  refreshQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
      return;
    }

    if (token) {
      promise.resolve(token);
    }
  });
  refreshQueue = [];
}

function isAuthBypassPath(url: string | undefined): boolean {
  if (!url) {
    return false;
  }

  return url.includes("/auth/login") || url.includes("/auth/refresh");
}

async function refreshAccessToken(): Promise<string> {
  const storedRefreshToken = getRefreshToken();
  if (!storedRefreshToken) {
    throw new ApiClientError("No refresh token available", "UNAUTHORIZED", 401);
  }

  const response = await refreshClient.post<ApiSuccessResponse<TokenResponse>>("/auth/refresh", {
    refresh_token: storedRefreshToken,
  });

  const tokens = response.data.data;
  setAuthTokens(tokens.access_token, tokens.refresh_token);
  return tokens.access_token;
}

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorResponse>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isAuthBypassPath(originalRequest.url)
    ) {
      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          refreshQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return apiClient(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newToken = await refreshAccessToken();
        processRefreshQueue(null, newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        processRefreshQueue(refreshError, null);
        clearAuthTokens();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    if (error.response?.data?.error) {
      const { message, error: errorBody } = error.response.data;
      throw new ApiClientError(
        message,
        errorBody.code,
        error.response.status,
        errorBody.details,
      );
    }

    throw new ApiClientError(
      error.message || "Network error",
      "NETWORK_ERROR",
      error.response?.status ?? 0,
    );
  },
);

export async function apiGet<T>(url: string): Promise<T> {
  const response = await apiClient.get<ApiSuccessResponse<T>>(url);
  return response.data.data;
}

export async function apiPost<T, B = unknown>(url: string, body?: B): Promise<T> {
  const response = await apiClient.post<ApiSuccessResponse<T>>(url, body);
  return response.data.data;
}

export async function apiPut<T, B = unknown>(url: string, body: B): Promise<T> {
  const response = await apiClient.put<ApiSuccessResponse<T>>(url, body);
  return response.data.data;
}

export async function apiDelete<T>(url: string): Promise<T> {
  const response = await apiClient.delete<ApiSuccessResponse<T>>(url);
  return response.data.data;
}

export { apiClient, clearAuthTokens, getRefreshToken, setAuthTokens };
