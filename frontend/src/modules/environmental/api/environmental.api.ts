import { apiDelete, apiGet, apiPost, apiPut } from "@/shared/services/api-client";
import type { PaginatedData } from "@/shared/types/api";

import type {
  CarbonTransaction,
  CarbonTransactionInput,
  DepartmentOption,
  EmissionFactor,
  EmissionFactorInput,
  EnvironmentalAnalytics,
  EnvironmentalGoal,
  EnvironmentalGoalInput,
  ListParams,
  ProductEsgInput,
  ProductEsgProfile,
} from "../types/environmental.types";

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

export const environmentalApi = {
  listDepartments: () => apiGet<DepartmentOption[]>("/environmental/departments"),

  listEmissionFactors: (params?: ListParams) =>
    apiGet<PaginatedData<EmissionFactor>>(`/environmental/emission-factors${buildQuery(params)}`),

  createEmissionFactor: (payload: EmissionFactorInput) =>
    apiPost<EmissionFactor, EmissionFactorInput>("/environmental/emission-factors", payload),

  updateEmissionFactor: (id: string, payload: Partial<EmissionFactorInput>) =>
    apiPut<EmissionFactor, Partial<EmissionFactorInput>>(
      `/environmental/emission-factors/${id}`,
      payload,
    ),

  deleteEmissionFactor: (id: string) => apiDelete<null>(`/environmental/emission-factors/${id}`),

  listCarbonTransactions: (params?: ListParams) =>
    apiGet<PaginatedData<CarbonTransaction>>(
      `/environmental/carbon-transactions${buildQuery(params)}`,
    ),

  createCarbonTransaction: (payload: CarbonTransactionInput) =>
    apiPost<CarbonTransaction, CarbonTransactionInput>(
      "/environmental/carbon-transactions",
      payload,
    ),

  updateCarbonTransaction: (id: string, payload: Partial<CarbonTransactionInput>) =>
    apiPut<CarbonTransaction, Partial<CarbonTransactionInput>>(
      `/environmental/carbon-transactions/${id}`,
      payload,
    ),

  deleteCarbonTransaction: (id: string) =>
    apiDelete<null>(`/environmental/carbon-transactions/${id}`),

  listGoals: (params?: ListParams) =>
    apiGet<PaginatedData<EnvironmentalGoal>>(`/environmental/goals${buildQuery(params)}`),

  createGoal: (payload: EnvironmentalGoalInput) =>
    apiPost<EnvironmentalGoal, EnvironmentalGoalInput>("/environmental/goals", payload),

  updateGoal: (id: string, payload: Partial<EnvironmentalGoalInput>) =>
    apiPut<EnvironmentalGoal, Partial<EnvironmentalGoalInput>>(
      `/environmental/goals/${id}`,
      payload,
    ),

  deleteGoal: (id: string) => apiDelete<null>(`/environmental/goals/${id}`),

  listProductEsgProfiles: (params?: ListParams) =>
    apiGet<PaginatedData<ProductEsgProfile>>(
      `/environmental/product-esg-profiles${buildQuery(params)}`,
    ),

  createProductEsgProfile: (payload: ProductEsgInput) =>
    apiPost<ProductEsgProfile, ProductEsgInput>("/environmental/product-esg-profiles", payload),

  updateProductEsgProfile: (id: string, payload: Partial<ProductEsgInput>) =>
    apiPut<ProductEsgProfile, Partial<ProductEsgInput>>(
      `/environmental/product-esg-profiles/${id}`,
      payload,
    ),

  deleteProductEsgProfile: (id: string) =>
    apiDelete<null>(`/environmental/product-esg-profiles/${id}`),

  getAnalytics: () => apiGet<EnvironmentalAnalytics>("/environmental/analytics/dashboard"),
};
