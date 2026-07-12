export type PolicyStatus = "ACTIVE" | "INACTIVE" | "ARCHIVED";
export type AcknowledgementStatus = "PENDING" | "ACKNOWLEDGED";
export type AuditStatus = "PLANNED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";
export type ComplianceSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type ComplianceIssueStatus = "OPEN" | "IN_PROGRESS" | "CLOSED" | "OVERDUE";

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
}

export interface Policy {
  id: string;
  title: string;
  version: string;
  description: string | null;
  effective_date: string;
  status: PolicyStatus;
  acknowledgement_count: number;
  pending_acknowledgements: number;
  created_at: string;
  updated_at: string;
}

export interface PolicyAcknowledgement {
  id: string;
  employee_id: string;
  employee_name: string | null;
  policy_id: string;
  policy_title: string | null;
  acknowledged_at: string | null;
  status: AcknowledgementStatus;
  created_at: string;
  updated_at: string;
}

export interface Audit {
  id: string;
  department_id: string;
  department_name: string | null;
  title: string;
  auditor_id: string;
  auditor_name: string | null;
  audit_date: string;
  status: AuditStatus;
  issue_count: number;
  open_issue_count: number;
  created_at: string;
  updated_at: string;
}

export interface ComplianceIssue {
  id: string;
  audit_id: string | null;
  audit_title: string | null;
  owner_id: string;
  owner_name: string | null;
  severity: ComplianceSeverity;
  description: string;
  due_date: string;
  status: ComplianceIssueStatus;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

export interface GovernanceAnalytics {
  governance_score: string;
  compliance_rate: string;
  open_issues: number;
  overdue_issues: number;
  policy_completion: string;
  total_policies: number;
  active_policies: number;
  total_acknowledgements: number;
  acknowledged_count: number;
  pending_acknowledgements: number;
  total_audits: number;
  completed_audits: number;
  closed_issues: number;
  total_issues: number;
}

export interface ListParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort?: string;
  order?: "asc" | "desc";
  status?: string;
  department_id?: string;
  policy_id?: string;
  employee_id?: string;
  audit_id?: string;
  owner_id?: string;
  severity?: string;
}

export interface PolicyInput {
  title: string;
  version: string;
  description?: string;
  effective_date: string;
  status?: PolicyStatus;
}

export interface AuditInput {
  department_id: string;
  title: string;
  auditor_id: string;
  audit_date: string;
  status?: AuditStatus;
}

export interface ComplianceIssueInput {
  audit_id?: string;
  owner_id: string;
  severity: ComplianceSeverity;
  description: string;
  due_date: string;
  status?: ComplianceIssueStatus;
}
