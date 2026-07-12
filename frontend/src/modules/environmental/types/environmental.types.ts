export type EntityStatus = "ACTIVE" | "INACTIVE" | "ARCHIVED";
export type GoalStatus = "NOT_STARTED" | "IN_PROGRESS" | "COMPLETED" | "OVERDUE";
export type TransactionStatus = "ACTIVE" | "ARCHIVED" | "CANCELLED";

export interface DepartmentOption {
  id: string;
  name: string;
  code: string;
}

export interface EmissionFactor {
  id: string;
  name: string;
  source_type: string;
  unit: string;
  co2_factor: string;
  description: string | null;
  status: EntityStatus;
  created_at: string;
  updated_at: string;
}

export interface CarbonTransaction {
  id: string;
  department_id: string;
  department_name: string | null;
  emission_factor_id: string;
  emission_factor_name: string | null;
  activity_name: string;
  quantity: string;
  unit: string;
  calculated_emission: string;
  transaction_date: string;
  status: TransactionStatus;
  created_at: string;
  updated_at: string;
}

export interface EnvironmentalGoal {
  id: string;
  department_id: string;
  department_name: string | null;
  title: string;
  target_value: string;
  current_value: string;
  progress_percentage: string;
  deadline: string;
  status: GoalStatus;
  created_at: string;
  updated_at: string;
}

export interface ProductEsgProfile {
  id: string;
  product_name: string;
  carbon_score: string;
  recyclability: string;
  supplier_score: string;
  notes: string | null;
  status: EntityStatus;
  created_at: string;
  updated_at: string;
}

export interface DepartmentCarbonTotal {
  department_id: string;
  department_name: string;
  total_emission: string;
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

export interface EnvironmentalAnalytics {
  department_carbon_totals: DepartmentCarbonTotal[];
  monthly_carbon_trend: MonthlyCarbonTrendPoint[];
  top_carbon_sources: TopCarbonSource[];
  goal_progress: GoalProgressItem[];
  total_emissions: string;
  active_goals: number;
  completed_goals: number;
}

export interface ListParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort?: string;
  order?: "asc" | "desc";
  status?: string;
  department_id?: string;
  source_type?: string;
}

export interface EmissionFactorInput {
  name: string;
  source_type: string;
  unit: string;
  co2_factor: string;
  description?: string;
  status?: EntityStatus;
}

export interface CarbonTransactionInput {
  department_id: string;
  emission_factor_id: string;
  activity_name: string;
  quantity: string;
  unit: string;
  transaction_date: string;
  status?: TransactionStatus;
}

export interface EnvironmentalGoalInput {
  department_id: string;
  title: string;
  target_value: string;
  current_value?: string;
  deadline: string;
  status?: GoalStatus;
}

export interface ProductEsgInput {
  product_name: string;
  carbon_score: string;
  recyclability: string;
  supplier_score: string;
  notes?: string;
  status?: EntityStatus;
}
