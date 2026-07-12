import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { governanceApi } from "../api/governance.api";
import type {
  AuditInput,
  ComplianceIssueInput,
  ListParams,
  PolicyInput,
} from "../types/governance.types";

const QUERY_KEYS = {
  departments: ["governance", "departments"] as const,
  employees: ["governance", "employees"] as const,
  analytics: ["governance", "analytics"] as const,
  policies: (params: ListParams) => ["governance", "policies", params] as const,
  audits: (params: ListParams) => ["governance", "audits", params] as const,
  issues: (params: ListParams) => ["governance", "issues", params] as const,
  acknowledgements: (params: ListParams) => ["governance", "acknowledgements", params] as const,
};

export function useGovernanceDepartments() {
  return useQuery({ queryKey: QUERY_KEYS.departments, queryFn: governanceApi.listDepartments });
}

export function useGovernanceEmployees() {
  return useQuery({ queryKey: QUERY_KEYS.employees, queryFn: governanceApi.listEmployees });
}

export function useGovernanceAnalytics() {
  return useQuery({ queryKey: QUERY_KEYS.analytics, queryFn: governanceApi.getAnalytics });
}

export function usePolicies(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.policies(params),
    queryFn: () => governanceApi.listPolicies(params),
  });
}

export function useAudits(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.audits(params),
    queryFn: () => governanceApi.listAudits(params),
  });
}

export function useComplianceIssues(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.issues(params),
    queryFn: () => governanceApi.listComplianceIssues(params),
  });
}

export function useAcknowledgements(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.acknowledgements(params),
    queryFn: () => governanceApi.listAcknowledgements(params),
  });
}

function invalidateGovernance(queryClient: ReturnType<typeof useQueryClient>) {
  void queryClient.invalidateQueries({ queryKey: ["governance"] });
  void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
}

export function usePolicyMutations() {
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: (payload: PolicyInput) => governanceApi.createPolicy(payload),
    onSuccess: () => invalidateGovernance(queryClient),
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<PolicyInput> }) =>
      governanceApi.updatePolicy(id, payload),
    onSuccess: () => invalidateGovernance(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => governanceApi.deletePolicy(id),
    onSuccess: () => invalidateGovernance(queryClient),
  });
  const acknowledge = useMutation({
    mutationFn: (policyId: string) => governanceApi.acknowledgePolicy(policyId),
    onSuccess: () => invalidateGovernance(queryClient),
  });
  return { create, update, remove, acknowledge };
}

export function useAuditMutations() {
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: (payload: AuditInput) => governanceApi.createAudit(payload),
    onSuccess: () => invalidateGovernance(queryClient),
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<AuditInput> }) =>
      governanceApi.updateAudit(id, payload),
    onSuccess: () => invalidateGovernance(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => governanceApi.deleteAudit(id),
    onSuccess: () => invalidateGovernance(queryClient),
  });
  return { create, update, remove };
}

export function useComplianceIssueMutations() {
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: (payload: ComplianceIssueInput) => governanceApi.createComplianceIssue(payload),
    onSuccess: () => invalidateGovernance(queryClient),
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<ComplianceIssueInput> }) =>
      governanceApi.updateComplianceIssue(id, payload),
    onSuccess: () => invalidateGovernance(queryClient),
  });
  const close = useMutation({
    mutationFn: (id: string) => governanceApi.closeComplianceIssue(id),
    onSuccess: () => invalidateGovernance(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => governanceApi.deleteComplianceIssue(id),
    onSuccess: () => invalidateGovernance(queryClient),
  });
  return { create, update, close, remove };
}
