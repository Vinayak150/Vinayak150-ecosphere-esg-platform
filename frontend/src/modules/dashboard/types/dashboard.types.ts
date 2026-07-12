import type { GoalStatus } from "@/modules/environmental/types/environmental.types";

export interface PillarScore {
  score: string | null;
  available: boolean;
  label: string;
}

export interface DepartmentRankingItem {
  rank: number;
  department_id: string;
  department_name: string;
  environmental_score: string;
  total_emission: string;
  goals_completed: number;
  goals_total: number;
}

export interface RecentCarbonTransaction {
  id: string;
  activity_name: string;
  department_name: string | null;
  emission_factor_name: string | null;
  calculated_emission: string;
  transaction_date: string;
  created_at: string;
}

export interface RecentActivity {
  id: string;
  action: string;
  entity: string;
  entity_id: string | null;
  message: string;
  created_at: string;
}

export interface DashboardNotification {
  id: string;
  type: string;
  title: string;
  message: string;
  severity: string;
  created_at: string;
  read: boolean;
}

export interface GoalProgressItem {
  goal_id: string;
  title: string;
  department_name: string;
  current_value: string;
  target_value: string;
  progress_percentage: string;
  status: GoalStatus;
  deadline: string;
}

export interface MonthlyCarbonTrendPoint {
  month: string;
  total_emission: string;
}

export interface TopCarbonSource {
  source_type: string;
  emission_factor_name: string;
  total_emission: string;
}

export interface QuickStat {
  key: string;
  label: string;
  value: string;
  trend: string | null;
}

export interface QuickAction {
  id: string;
  label: string;
  description: string;
  route: string;
  permission: string;
  enabled: boolean;
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

export interface EmployeeBadgeUnlock {
  id: string;
  badge_id: string;
  badge_name: string | null;
  badge_icon: string | null;
  employee_id: string;
  employee_name: string | null;
  earned_at: string;
}

export interface ChallengeProgressItem {
  id: string;
  title: string;
  category: string;
  xp: number;
  status: string;
  participation_count: number;
  approved_count: number;
  deadline: string;
}

export interface DashboardData {
  overallESG: string;
  environmentalScore: PillarScore;
  socialScore: PillarScore;
  governanceScore: PillarScore;
  departmentRanking: DepartmentRankingItem[];
  recentCarbonTransactions: RecentCarbonTransaction[];
  recentActivity: RecentActivity[];
  notifications: DashboardNotification[];
  goalProgress: GoalProgressItem[];
  monthlyCarbonTrend: MonthlyCarbonTrendPoint[];
  topCarbonSources: TopCarbonSource[];
  quickStats: QuickStat[];
  quickActions: QuickAction[];
  topPerformers: LeaderboardEntry[];
  xpLeaderboard: LeaderboardEntry[];
  recentBadgeUnlocks: EmployeeBadgeUnlock[];
  challengeProgress: ChallengeProgressItem[];
}
