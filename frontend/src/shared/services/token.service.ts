import { API_BASE_URL, REFRESH_TOKEN_STORAGE_KEY, TOKEN_STORAGE_KEY } from "@/shared/constants/app";

export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);
}

export function setAuthTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, refreshToken);
  window.dispatchEvent(new CustomEvent("ecosphere:auth:tokens-updated"));
}

export function clearAuthTokens(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
  window.dispatchEvent(new CustomEvent("ecosphere:auth:tokens-cleared"));
}

export function hasAccessToken(): boolean {
  return Boolean(getAccessToken());
}

export { API_BASE_URL };
