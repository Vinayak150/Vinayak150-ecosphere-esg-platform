export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export const APP_NAME = "EcoSphere";

export const TOKEN_STORAGE_KEY = "ecosphere_access_token";
export const REFRESH_TOKEN_STORAGE_KEY = "ecosphere_refresh_token";

export const ROUTES = {
  login: "/login",
  home: "/",
  environmental: "/environmental",
  social: "/social",
  governance: "/governance",
  gamification: "/gamification",
} as const;
