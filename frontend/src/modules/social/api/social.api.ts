import { apiDelete, apiGet, apiPost, apiPut } from "@/shared/services/api-client";
import type { PaginatedData } from "@/shared/types/api";

import type {
  CsrActivity,
  CsrActivityInput,
  DepartmentOption,
  ListParams,
  Participation,
  ParticipationInput,
  SocialAnalytics,
} from "../types/social.types";

function buildQuery(params: ListParams = {}): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

export const socialApi = {
  listDepartments: () => apiGet<DepartmentOption[]>("/social/departments"),

  listCsrActivities: (params?: ListParams) =>
    apiGet<PaginatedData<CsrActivity>>(`/social/csr-activities${buildQuery(params)}`),

  createCsrActivity: (payload: CsrActivityInput) =>
    apiPost<CsrActivity, CsrActivityInput>("/social/csr-activities", payload),

  updateCsrActivity: (id: string, payload: Partial<CsrActivityInput>) =>
    apiPut<CsrActivity, Partial<CsrActivityInput>>(`/social/csr-activities/${id}`, payload),

  deleteCsrActivity: (id: string) => apiDelete<null>(`/social/csr-activities/${id}`),

  listParticipations: (params?: ListParams) =>
    apiGet<PaginatedData<Participation>>(`/social/participation${buildQuery(params)}`),

  createParticipation: (payload: ParticipationInput) =>
    apiPost<Participation, ParticipationInput>("/social/participation", payload),

  updateParticipation: (id: string, payload: { proof_file?: string }) =>
    apiPut<Participation, { proof_file?: string }>(`/social/participation/${id}`, payload),

  approveParticipation: (id: string) =>
    apiPost<Participation>(`/social/participation/${id}/approve`),

  rejectParticipation: (id: string, rejection_reason?: string) =>
    apiPost<Participation, { rejection_reason?: string }>(
      `/social/participation/${id}/reject`,
      { rejection_reason },
    ),

  deleteParticipation: (id: string) => apiDelete<null>(`/social/participation/${id}`),

  getAnalytics: () => apiGet<SocialAnalytics>("/social/analytics/dashboard"),
};
