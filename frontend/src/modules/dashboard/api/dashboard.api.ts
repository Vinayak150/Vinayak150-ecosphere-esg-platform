import { apiGet } from "@/shared/services/api-client";

import type { DashboardData } from "../types/dashboard.types";

export function getDashboard(): Promise<DashboardData> {
  return apiGet<DashboardData>("/dashboard");
}
