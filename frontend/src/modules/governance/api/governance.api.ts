import { apiDelete, apiGet, apiPost, apiPut } from "@/shared/services/api-client";
import type { PaginatedData } from "@/shared/types/api";

import type {
  Audit,
  AuditInput,
  ComplianceIssue,
  ComplianceIssueInput,
  DepartmentOption,
  EmployeeOption,
  GovernanceAnalytics,
  ListParams,
  Policy,
  PolicyAcknowledgement,
  PolicyInput,
} from "../types/governance.types";

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

export const governanceApi = {
  listDepartments: () => apiGet<DepartmentOption[]>("/governance/departments"),

  listEmployees: () => apiGet<EmployeeOption[]>("/governance/employees"),

  listPolicies: (params?: ListParams) =>
    apiGet<PaginatedData<Policy>>(`/governance/policies${buildQuery(params)}`),

  createPolicy: (payload: PolicyInput) =>
    apiPost<Policy, PolicyInput>("/governance/policies", payload),

  updatePolicy: (id: string, payload: Partial<PolicyInput>) =>
    apiPut<Policy, Partial<PolicyInput>>(`/governance/policies/${id}`, payload),

  deletePolicy: (id: string) => apiDelete<null>(`/governance/policies/${id}`),

  listAcknowledgements: (params?: ListParams) =>
    apiGet<PaginatedData<PolicyAcknowledgement>>(
      `/governance/policy-acknowledgements${buildQuery(params)}`,
    ),

  acknowledgePolicy: (policy_id: string) =>
    apiPost<PolicyAcknowledgement, { policy_id: string }>(
      "/governance/policy-acknowledgements",
      { policy_id },
    ),

  listAudits: (params?: ListParams) =>
    apiGet<PaginatedData<Audit>>(`/governance/audits${buildQuery(params)}`),

  createAudit: (payload: AuditInput) =>
    apiPost<Audit, AuditInput>("/governance/audits", payload),

  updateAudit: (id: string, payload: Partial<AuditInput>) =>
    apiPut<Audit, Partial<AuditInput>>(`/governance/audits/${id}`, payload),

  deleteAudit: (id: string) => apiDelete<null>(`/governance/audits/${id}`),

  listComplianceIssues: (params?: ListParams) =>
    apiGet<PaginatedData<ComplianceIssue>>(
      `/governance/compliance-issues${buildQuery(params)}`,
    ),

  createComplianceIssue: (payload: ComplianceIssueInput) =>
    apiPost<ComplianceIssue, ComplianceIssueInput>(
      "/governance/compliance-issues",
      payload,
    ),

  updateComplianceIssue: (id: string, payload: Partial<ComplianceIssueInput>) =>
    apiPut<ComplianceIssue, Partial<ComplianceIssueInput>>(
      `/governance/compliance-issues/${id}`,
      payload,
    ),

  closeComplianceIssue: (id: string) =>
    apiPost<ComplianceIssue>(`/governance/compliance-issues/${id}/close`),

  deleteComplianceIssue: (id: string) =>
    apiDelete<null>(`/governance/compliance-issues/${id}`),

  getAnalytics: () => apiGet<GovernanceAnalytics>("/governance/analytics/dashboard"),
};
