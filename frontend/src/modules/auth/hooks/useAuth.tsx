import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { getCurrentUser, login as loginRequest, logout as logoutRequest } from "../api/auth.api";
import type { LoginRequest, User } from "../types/auth.types";
import { hasAccessToken } from "@/shared/services/token.service";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (!hasAccessToken()) {
      setUser(null);
      return;
    }

    const currentUser = await getCurrentUser();
    setUser(currentUser);
  }, []);

  useEffect(() => {
    const initialize = async () => {
      try {
        await refreshUser();
      } catch {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    void initialize();
  }, [refreshUser]);

  useEffect(() => {
    const handleTokensCleared = () => {
      setUser(null);
    };

    const handleTokensUpdated = () => {
      void refreshUser();
    };

    window.addEventListener("ecosphere:auth:tokens-cleared", handleTokensCleared);
    window.addEventListener("ecosphere:auth:tokens-updated", handleTokensUpdated);

    return () => {
      window.removeEventListener("ecosphere:auth:tokens-cleared", handleTokensCleared);
      window.removeEventListener("ecosphere:auth:tokens-updated", handleTokensUpdated);
    };
  }, [refreshUser]);

  const login = useCallback(async (credentials: LoginRequest) => {
    const response = await loginRequest(credentials);
    setUser(response.user);
  }, []);

  const logout = useCallback(async () => {
    try {
      await logoutRequest();
    } finally {
      setUser(null);
    }
  }, []);

  const hasPermission = useCallback(
    (permission: string) => user?.permissions.includes(permission) ?? false,
    [user],
  );

  const hasRole = useCallback(
    (role: string) => user?.roles.some((item) => item.name === role) ?? false,
    [user],
  );

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      logout,
      hasPermission,
      hasRole,
      refreshUser,
    }),
    [user, isLoading, login, logout, hasPermission, hasRole, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
