import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { environmentalApi } from "../api/environmental.api";
import type {
  CarbonTransactionInput,
  EmissionFactorInput,
  EnvironmentalGoalInput,
  ListParams,
  ProductEsgInput,
} from "../types/environmental.types";

const QUERY_KEYS = {
  departments: ["environmental", "departments"] as const,
  analytics: ["environmental", "analytics"] as const,
  emissionFactors: (params: ListParams) => ["environmental", "emission-factors", params] as const,
  carbonTransactions: (params: ListParams) =>
    ["environmental", "carbon-transactions", params] as const,
  goals: (params: ListParams) => ["environmental", "goals", params] as const,
  productEsg: (params: ListParams) => ["environmental", "product-esg", params] as const,
};

export function useDepartments() {
  return useQuery({
    queryKey: QUERY_KEYS.departments,
    queryFn: environmentalApi.listDepartments,
  });
}

export function useEnvironmentalAnalytics() {
  return useQuery({
    queryKey: QUERY_KEYS.analytics,
    queryFn: environmentalApi.getAnalytics,
  });
}

export function useEmissionFactors(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.emissionFactors(params),
    queryFn: () => environmentalApi.listEmissionFactors(params),
  });
}

export function useCarbonTransactions(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.carbonTransactions(params),
    queryFn: () => environmentalApi.listCarbonTransactions(params),
  });
}

export function useEnvironmentalGoals(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.goals(params),
    queryFn: () => environmentalApi.listGoals(params),
  });
}

export function useProductEsgProfiles(params: ListParams) {
  return useQuery({
    queryKey: QUERY_KEYS.productEsg(params),
    queryFn: () => environmentalApi.listProductEsgProfiles(params),
  });
}

function invalidateEnvironmental(queryClient: ReturnType<typeof useQueryClient>) {
  void queryClient.invalidateQueries({ queryKey: ["environmental"] });
}

export function useEmissionFactorMutations() {
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: (payload: EmissionFactorInput) => environmentalApi.createEmissionFactor(payload),
    onSuccess: () => invalidateEnvironmental(queryClient),
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<EmissionFactorInput> }) =>
      environmentalApi.updateEmissionFactor(id, payload),
    onSuccess: () => invalidateEnvironmental(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => environmentalApi.deleteEmissionFactor(id),
    onSuccess: () => invalidateEnvironmental(queryClient),
  });
  return { create, update, remove };
}

export function useCarbonTransactionMutations() {
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: (payload: CarbonTransactionInput) =>
      environmentalApi.createCarbonTransaction(payload),
    onSuccess: () => invalidateEnvironmental(queryClient),
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<CarbonTransactionInput> }) =>
      environmentalApi.updateCarbonTransaction(id, payload),
    onSuccess: () => invalidateEnvironmental(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => environmentalApi.deleteCarbonTransaction(id),
    onSuccess: () => invalidateEnvironmental(queryClient),
  });
  return { create, update, remove };
}

export function useGoalMutations() {
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: (payload: EnvironmentalGoalInput) => environmentalApi.createGoal(payload),
    onSuccess: () => invalidateEnvironmental(queryClient),
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<EnvironmentalGoalInput> }) =>
      environmentalApi.updateGoal(id, payload),
    onSuccess: () => invalidateEnvironmental(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => environmentalApi.deleteGoal(id),
    onSuccess: () => invalidateEnvironmental(queryClient),
  });
  return { create, update, remove };
}

export function useProductEsgMutations() {
  const queryClient = useQueryClient();
  const create = useMutation({
    mutationFn: (payload: ProductEsgInput) => environmentalApi.createProductEsgProfile(payload),
    onSuccess: () => invalidateEnvironmental(queryClient),
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<ProductEsgInput> }) =>
      environmentalApi.updateProductEsgProfile(id, payload),
    onSuccess: () => invalidateEnvironmental(queryClient),
  });
  const remove = useMutation({
    mutationFn: (id: string) => environmentalApi.deleteProductEsgProfile(id),
    onSuccess: () => invalidateEnvironmental(queryClient),
  });
  return { create, update, remove };
}
