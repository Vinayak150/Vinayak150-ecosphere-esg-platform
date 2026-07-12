import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { socialApi } from "../api/social.api";
import type { CsrActivityInput, ListParams, ParticipationInput } from "../types/social.types";

const QUERY_KEYS = {
  departments: ["social", "departments"] as const,
  analytics: ["social", "analytics"] as const,
  activities: (params: ListParams) => ["social", "activities", params] as const,
  participations: (params: ListParams) => ["social", "participations", params] as const,
};

export function useSocialDepartments() {
  return useQuery({ queryKey: QUERY_KEYS.departments, queryFn: socialApi.listDepartments });
}

export function useSocialAnalytics() {
  return useQuery({ queryKey: QUERY_KEYS.analytics, queryFn: socialApi.getAnalytics });
}

export function useCsrActivities(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.activities(params),
    queryFn: () => socialApi.listCsrActivities(params),
  });
}

export function useParticipations(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.participations(params),
    queryFn: () => socialApi.listParticipations(params),
  });
}

function invalidateSocial(queryClient: ReturnType<typeof useQueryClient>) {
  void queryClient.invalidateQueries({ queryKey: ["social"] });
  void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
}

export function useCsrActivityMutations() {
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: (payload: CsrActivityInput) => socialApi.createCsrActivity(payload),
    onSuccess: () => invalidateSocial(queryClient),
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<CsrActivityInput> }) =>
      socialApi.updateCsrActivity(id, payload),
    onSuccess: () => invalidateSocial(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => socialApi.deleteCsrActivity(id),
    onSuccess: () => invalidateSocial(queryClient),
  });
  return { create, update, remove };
}

export function useParticipationMutations() {
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: (payload: ParticipationInput) => socialApi.createParticipation(payload),
    onSuccess: () => invalidateSocial(queryClient),
  });
  const update = useMutation({
    mutationFn: ({ id, proof_file }: { id: string; proof_file?: string }) =>
      socialApi.updateParticipation(id, { proof_file }),
    onSuccess: () => invalidateSocial(queryClient),
  });
  const approve = useMutation({
    mutationFn: (id: string) => socialApi.approveParticipation(id),
    onSuccess: () => invalidateSocial(queryClient),
  });
  const reject = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      socialApi.rejectParticipation(id, reason),
    onSuccess: () => invalidateSocial(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => socialApi.deleteParticipation(id),
    onSuccess: () => invalidateSocial(queryClient),
  });
  return { create, update, approve, reject, remove };
}
