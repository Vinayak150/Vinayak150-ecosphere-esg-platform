export type ChallengeStatus =
  | "DRAFT"
  | "ACTIVE"
  | "UNDER_REVIEW"
  | "COMPLETED"
  | "ARCHIVED";
export type ChallengeDifficulty = "EASY" | "MEDIUM" | "HARD" | "EXPERT";
export type ParticipationApproval = "PENDING" | "SUBMITTED" | "APPROVED" | "REJECTED";
export type BadgeStatus = "ACTIVE" | "INACTIVE" | "ARCHIVED";
export type RewardStatus = "ACTIVE" | "INACTIVE" | "OUT_OF_STOCK" | "ARCHIVED";

export interface DepartmentOption {
  id: string;
  name: string;
  code: string;
}

export interface EmployeeOption {
  id: string;
  name: string;
  email: string;
  department_name: string | null;
  total_xp: number;
}

export interface Challenge {
  id: string;
  title: string;
  category: string;
  description: string | null;
  xp: number;
  difficulty: ChallengeDifficulty;
  evidence_required: boolean;
  deadline: string;
  status: ChallengeStatus;
  participation_count: number;
  approved_count: number;
  created_at: string;
  updated_at: string;
}

export interface Participation {
  id: string;
  employee_id: string;
  employee_name: string | null;
  department_name: string | null;
  challenge_id: string;
  challenge_title: string | null;
  progress: number;
  proof_file: string | null;
  approval_status: ParticipationApproval;
  xp_awarded: number;
  completion_date: string | null;
  rejection_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface Badge {
  id: string;
  name: string;
  description: string | null;
  unlock_rule: Record<string, unknown>;
  icon: string | null;
  status: BadgeStatus;
  earned_count: number;
  created_at: string;
  updated_at: string;
}

export interface EmployeeBadge {
  id: string;
  badge_id: string;
  badge_name: string | null;
  badge_icon: string | null;
  employee_id: string;
  employee_name: string | null;
  earned_at: string;
  created_at: string;
  updated_at: string;
}

export interface Reward {
  id: string;
  name: string;
  description: string | null;
  points_required: number;
  stock: number;
  status: RewardStatus;
  redemption_count: number;
  created_at: string;
  updated_at: string;
}

export interface RewardRedemption {
  id: string;
  reward_id: string;
  reward_name: string | null;
  employee_id: string;
  employee_name: string | null;
  redeemed_points: number;
  redeemed_at: string;
  created_at: string;
  updated_at: string;
}

export interface LeaderboardEntry {
  rank: number;
  employee_id: string;
  employee_name: string;
  department_id: string | null;
  department_name: string | null;
  total_xp: number;
  badge_count: number;
}

export interface DepartmentLeaderboardEntry {
  rank: number;
  department_id: string;
  department_name: string;
  total_xp: number;
  employee_count: number;
  average_xp: string;
}

export interface BadgeDistributionItem {
  badge_id: string;
  badge_name: string;
  earned_count: number;
}

export interface GamificationAnalytics {
  total_xp: number;
  total_challenges: number;
  active_challenges: number;
  completed_challenges: number;
  challenge_completion_rate: string;
  total_badges: number;
  total_badge_awards: number;
  badge_distribution: BadgeDistributionItem[];
  top_employees: LeaderboardEntry[];
  top_departments: DepartmentLeaderboardEntry[];
  pending_reviews: number;
}

export interface ListParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort?: string;
  order?: "asc" | "desc";
  status?: string;
  category?: string;
  difficulty?: string;
  challenge_id?: string;
  employee_id?: string;
  approval_status?: string;
}

export interface ChallengeInput {
  title: string;
  category: string;
  description?: string;
  xp?: number;
  difficulty?: ChallengeDifficulty;
  evidence_required?: boolean;
  deadline: string;
  status?: ChallengeStatus;
}

export interface ParticipationJoinInput {
  challenge_id: string;
}

export interface ParticipationSubmitInput {
  progress?: number;
  proof_file?: string;
}

export interface BadgeInput {
  name: string;
  description?: string;
  unlock_rule?: Record<string, unknown>;
  icon?: string;
  status?: BadgeStatus;
}

export interface RewardInput {
  name: string;
  description?: string;
  points_required: number;
  stock?: number;
  status?: RewardStatus;
}

export interface RewardRedemptionInput {
  reward_id: string;
}
