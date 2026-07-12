export type UserStatus = "ACTIVE" | "INACTIVE" | "LOCKED";

export interface Role {
  id: string;
  name: string;
  slug: string;
}

export interface EmployeeSummary {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  designation: string | null;
  department_id: string | null;
}

export interface User {
  id: string;
  email: string;
  status: UserStatus;
  last_login: string | null;
  roles: Role[];
  permissions: string[];
  employee: EmployeeSummary | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
  user: User;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface SessionInfo {
  user_id: string;
  email: string;
  roles: string[];
  permissions: string[];
  issued_at: string;
  expires_at: string | null;
  is_active: boolean;
}

export interface SessionResponse {
  session: SessionInfo;
  user: User;
}
