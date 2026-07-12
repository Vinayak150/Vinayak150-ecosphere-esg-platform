import { apiDelete, apiGet, apiPost, apiPut } from "@/shared/services/api-client";
import type { PaginatedData } from "@/shared/types/api";

import type {
  Badge,
  BadgeInput,
  Challenge,
  ChallengeInput,
  DepartmentOption,
  EmployeeBadge,
  GamificationAnalytics,
  LeaderboardEntry,
  ListParams,
  Participation,
  ParticipationJoinInput,
  ParticipationSubmitInput,
  Reward,
  RewardInput,
  RewardRedemption,
  RewardRedemptionInput,
  DepartmentLeaderboardEntry,
} from "../types/gamification.types";

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

export const gamificationApi = {
  listDepartments: () => apiGet<DepartmentOption[]>("/gamification/departments"),

  listEmployees: () => apiGet<import("../types/gamification.types").EmployeeOption[]>(
    "/gamification/employees",
  ),

  listChallenges: (params?: ListParams) =>
    apiGet<PaginatedData<Challenge>>(`/gamification/challenges${buildQuery(params)}`),

  createChallenge: (payload: ChallengeInput) =>
    apiPost<Challenge, ChallengeInput>("/gamification/challenges", payload),

  updateChallenge: (id: string, payload: Partial<ChallengeInput>) =>
    apiPut<Challenge, Partial<ChallengeInput>>(`/gamification/challenges/${id}`, payload),

  deleteChallenge: (id: string) => apiDelete<null>(`/gamification/challenges/${id}`),

  listParticipations: (params?: ListParams) =>
    apiGet<PaginatedData<Participation>>(`/gamification/participation${buildQuery(params)}`),

  joinChallenge: (payload: ParticipationJoinInput) =>
    apiPost<Participation, ParticipationJoinInput>("/gamification/participation", payload),

  submitParticipation: (id: string, payload: ParticipationSubmitInput) =>
    apiPut<Participation, ParticipationSubmitInput>(
      `/gamification/participation/${id}`,
      payload,
    ),

  approveParticipation: (id: string) =>
    apiPost<Participation>(`/gamification/participation/${id}/approve`),

  rejectParticipation: (id: string, rejection_reason?: string) =>
    apiPost<Participation, { rejection_reason?: string }>(
      `/gamification/participation/${id}/reject`,
      { rejection_reason },
    ),

  deleteParticipation: (id: string) => apiDelete<null>(`/gamification/participation/${id}`),

  listBadges: (params?: ListParams) =>
    apiGet<PaginatedData<Badge>>(`/gamification/badges${buildQuery(params)}`),

  createBadge: (payload: BadgeInput) =>
    apiPost<Badge, BadgeInput>("/gamification/badges", payload),

  updateBadge: (id: string, payload: Partial<BadgeInput>) =>
    apiPut<Badge, Partial<BadgeInput>>(`/gamification/badges/${id}`, payload),

  deleteBadge: (id: string) => apiDelete<null>(`/gamification/badges/${id}`),

  listEmployeeBadges: (params?: ListParams) =>
    apiGet<PaginatedData<EmployeeBadge>>(`/gamification/employee-badges${buildQuery(params)}`),

  listRewards: (params?: ListParams) =>
    apiGet<PaginatedData<Reward>>(`/gamification/rewards${buildQuery(params)}`),

  createReward: (payload: RewardInput) =>
    apiPost<Reward, RewardInput>("/gamification/rewards", payload),

  updateReward: (id: string, payload: Partial<RewardInput>) =>
    apiPut<Reward, Partial<RewardInput>>(`/gamification/rewards/${id}`, payload),

  deleteReward: (id: string) => apiDelete<null>(`/gamification/rewards/${id}`),

  redeemReward: (payload: RewardRedemptionInput) =>
    apiPost<RewardRedemption, RewardRedemptionInput>("/gamification/rewards/redeem", payload),

  getCompanyLeaderboard: (limit = 20) =>
    apiGet<LeaderboardEntry[]>(`/gamification/leaderboard/company?limit=${limit}`),

  getDepartmentLeaderboard: (limit = 20) =>
    apiGet<DepartmentLeaderboardEntry[]>(
      `/gamification/leaderboard/department?limit=${limit}`,
    ),

  getAnalytics: () => apiGet<GamificationAnalytics>("/gamification/analytics/dashboard"),
};
