import {
  apiGet,
  apiPost,
} from "@/shared/services/api-client";
import {
  clearAuthTokens,
  getRefreshToken,
  setAuthTokens,
} from "@/shared/services/token.service";

import type {
  LoginRequest,
  RefreshTokenRequest,
  TokenResponse,
  User,
} from "../types/auth.types";

export async function login(request: LoginRequest): Promise<TokenResponse> {
  const response = await apiPost<TokenResponse, LoginRequest>("/auth/login", request);
  setAuthTokens(response.access_token, response.refresh_token);
  return response;
}

export async function refreshToken(): Promise<TokenResponse> {
  const storedRefreshToken = getRefreshToken();
  if (!storedRefreshToken) {
    throw new Error("No refresh token available");
  }

  const response = await apiPost<TokenResponse, RefreshTokenRequest>("/auth/refresh", {
    refresh_token: storedRefreshToken,
  });
  setAuthTokens(response.access_token, response.refresh_token);
  return response;
}

export async function logout(): Promise<void> {
  const storedRefreshToken = getRefreshToken();
  try {
    await apiPost<void, RefreshTokenRequest | undefined>(
      "/auth/logout",
      storedRefreshToken ? { refresh_token: storedRefreshToken } : undefined,
    );
  } finally {
    clearAuthTokens();
  }
}

export async function getCurrentUser(): Promise<User> {
  return apiGet<User>("/auth/me");
}
