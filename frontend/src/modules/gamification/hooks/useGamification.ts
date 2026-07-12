import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { gamificationApi } from "../api/gamification.api";
import type {
  BadgeInput,
  ChallengeInput,
  ListParams,
  ParticipationJoinInput,
  ParticipationSubmitInput,
  RewardInput,
  RewardRedemptionInput,
} from "../types/gamification.types";

const QUERY_KEYS = {
  departments: ["gamification", "departments"] as const,
  analytics: ["gamification", "analytics"] as const,
  challenges: (params: ListParams) => ["gamification", "challenges", params] as const,
  participations: (params: ListParams) => ["gamification", "participations", params] as const,
  badges: (params: ListParams) => ["gamification", "badges", params] as const,
  employeeBadges: (params: ListParams) => ["gamification", "employee-badges", params] as const,
  rewards: (params: ListParams) => ["gamification", "rewards", params] as const,
  companyLeaderboard: ["gamification", "leaderboard", "company"] as const,
  departmentLeaderboard: ["gamification", "leaderboard", "department"] as const,
};

function invalidateGamification(queryClient: ReturnType<typeof useQueryClient>) {
  void queryClient.invalidateQueries({ queryKey: ["gamification"] });
  void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
}

export function useGamificationDepartments() {
  return useQuery({
    queryKey: QUERY_KEYS.departments,
    queryFn: gamificationApi.listDepartments,
  });
}

export function useGamificationAnalytics() {
  return useQuery({ queryKey: QUERY_KEYS.analytics, queryFn: gamificationApi.getAnalytics });
}

export function useChallenges(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.challenges(params),
    queryFn: () => gamificationApi.listChallenges(params),
  });
}

export function useParticipations(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.participations(params),
    queryFn: () => gamificationApi.listParticipations(params),
  });
}

export function useBadges(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.badges(params),
    queryFn: () => gamificationApi.listBadges(params),
  });
}

export function useEmployeeBadges(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.employeeBadges(params),
    queryFn: () => gamificationApi.listEmployeeBadges(params),
  });
}

export function useRewards(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.rewards(params),
    queryFn: () => gamificationApi.listRewards(params),
  });
}

export function useCompanyLeaderboard() {
  return useQuery({
    queryKey: QUERY_KEYS.companyLeaderboard,
    queryFn: () => gamificationApi.getCompanyLeaderboard(20),
  });
}

export function useDepartmentLeaderboard() {
  return useQuery({
    queryKey: QUERY_KEYS.departmentLeaderboard,
    queryFn: () => gamificationApi.getDepartmentLeaderboard(20),
  });
}

export function useChallengeMutations() {
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: (payload: ChallengeInput) => gamificationApi.createChallenge(payload),
    onSuccess: () => invalidateGamification(queryClient),
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<ChallengeInput> }) =>
      gamificationApi.updateChallenge(id, payload),
    onSuccess: () => invalidateGamification(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => gamificationApi.deleteChallenge(id),
    onSuccess: () => invalidateGamification(queryClient),
  });
  return { create, update, remove };
}

export function useParticipationMutations() {
  const queryClient = useQueryClient();
  const join = useMutation({
    mutationFn: (payload: ParticipationJoinInput) => gamificationApi.joinChallenge(payload),
    onSuccess: () => invalidateGamification(queryClient),
  });
  const submit = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: ParticipationSubmitInput }) =>
      gamificationApi.submitParticipation(id, payload),
    onSuccess: () => invalidateGamification(queryClient),
  });
  const approve = useMutation({
    mutationFn: (id: string) => gamificationApi.approveParticipation(id),
    onSuccess: () => invalidateGamification(queryClient),
  });
  const reject = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      gamificationApi.rejectParticipation(id, reason),
    onSuccess: () => invalidateGamification(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => gamificationApi.deleteParticipation(id),
    onSuccess: () => invalidateGamification(queryClient),
  });
  return { join, submit, approve, reject, remove };
}

export function useBadgeMutations() {
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: (payload: BadgeInput) => gamificationApi.createBadge(payload),
    onSuccess: () => invalidateGamification(queryClient),
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<BadgeInput> }) =>
      gamificationApi.updateBadge(id, payload),
    onSuccess: () => invalidateGamification(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => gamificationApi.deleteBadge(id),
    onSuccess: () => invalidateGamification(queryClient),
  });
  return { create, update, remove };
}

export function useRewardMutations() {
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: (payload: RewardInput) => gamificationApi.createReward(payload),
    onSuccess: () => invalidateGamification(queryClient),
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<RewardInput> }) =>
      gamificationApi.updateReward(id, payload),
    onSuccess: () => invalidateGamification(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => gamificationApi.deleteReward(id),
    onSuccess: () => invalidateGamification(queryClient),
  });
  const redeem = useMutation({
    mutationFn: (payload: RewardRedemptionInput) => gamificationApi.redeemReward(payload),
    onSuccess: () => invalidateGamification(queryClient),
  });
  return { create, update, remove, redeem };
}
