export type CSRActivityStatus = "ACTIVE" | "COMPLETED" | "CANCELLED" | "ARCHIVED";
export type ApprovalStatus = "PENDING" | "APPROVED" | "REJECTED";

export interface DepartmentOption {
  id: string;
  name: string;
  code: string;
}

export interface CsrActivity {
  id: string;
  title: string;
  category: string;
  department_id: string;
  department_name: string | null;
  description: string | null;
  start_date: string;
  end_date: string;
  points: number;
  evidence_required: boolean;
  status: CSRActivityStatus;
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
  csr_activity_id: string;
  csr_activity_title: string | null;
  proof_file: string | null;
  approval_status: ApprovalStatus;
  points_earned: number;
  completion_date: string | null;
  rejection_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface DepartmentParticipation {
  department_id: string;
  department_name: string;
  participation_count: number;
  approved_count: number;
  participation_rate: string;
}

export interface MonthlyCsrTrendPoint {
  month: string;
  participation_count: number;
  approved_count: number;
}

export interface TopParticipatingDepartment {
  department_id: string;
  department_name: string;
  approved_participations: number;
  total_points: number;
}

export interface SocialAnalytics {
  participation_rate: string;
  total_employees: number;
  total_participations: number;
  approved_participations: number;
  pending_approvals: number;
  social_score: string;
  department_participation: DepartmentParticipation[];
  monthly_csr_trend: MonthlyCsrTrendPoint[];
  top_participating_departments: TopParticipatingDepartment[];
  active_csr_activities: number;
  completed_csr_activities: number;
}

export interface ListParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort?: string;
  order?: "asc" | "desc";
  status?: string;
  department_id?: string;
  category?: string;
  approval_status?: string;
  csr_activity_id?: string;
}

export interface CsrActivityInput {
  title: string;
  category: string;
  department_id: string;
  description?: string;
  start_date: string;
  end_date: string;
  points?: number;
  evidence_required?: boolean;
  status?: CSRActivityStatus;
}

export interface ParticipationInput {
  csr_activity_id: string;
  proof_file?: string;
}
