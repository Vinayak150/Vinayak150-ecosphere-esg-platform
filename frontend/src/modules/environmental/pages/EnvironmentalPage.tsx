import { useMemo, useState } from "react";
import { Leaf, Plus, Search, Trash2 } from "lucide-react";

import { usePermission } from "@/modules/auth/hooks/usePermission";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Select } from "@/shared/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { Textarea } from "@/shared/components/ui/textarea";
import { ErrorState, LoadingSkeleton } from "@/shared/components/feedback/states";
import { useToast } from "@/shared/hooks/use-toast";

import { EnvironmentalCharts } from "../components/EnvironmentalCharts";
import {
  useCarbonTransactionMutations,
  useCarbonTransactions,
  useDepartments,
  useEmissionFactorMutations,
  useEmissionFactors,
  useEnvironmentalAnalytics,
  useEnvironmentalGoals,
  useGoalMutations,
  useProductEsgMutations,
  useProductEsgProfiles,
} from "../hooks/useEnvironmental";
import type {
  CarbonTransaction,
  CarbonTransactionInput,
  EmissionFactor,
  EmissionFactorInput,
  EnvironmentalGoal,
  EnvironmentalGoalInput,
  ProductEsgInput,
  ProductEsgProfile,
} from "../types/environmental.types";

function formatNumber(value: string | number, decimals = 2): string {
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function PaginationBar({
  page,
  pages,
  total,
  onPageChange,
}: {
  page: number;
  pages: number;
  total: number;
  onPageChange: (page: number) => void;
}) {
  return (
    <div className="flex items-center justify-between border-t px-4 py-3 text-sm text-muted-foreground">
      <span>
        Page {page} of {pages || 1} ({total} total)
      </span>
      <div className="flex gap-2">
        <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={page >= pages}
          onClick={() => onPageChange(page + 1)}
        >
          Next
        </Button>
      </div>
    </div>
  );
}

function goalStatusVariant(status: string): "default" | "secondary" | "destructive" {
  if (status === "COMPLETED") return "default";
  if (status === "OVERDUE") return "destructive";
  return "secondary";
}

export function EnvironmentalPage() {
  const canWrite = usePermission("carbon:write");
  const { toast } = useToast();

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const listParams = useMemo(() => ({ page, page_size: 10, search: search || undefined }), [page, search]);

  const { data: departments = [] } = useDepartments();
  const { data: analytics, isLoading: analyticsLoading, isError, refetch } =
    useEnvironmentalAnalytics();
  const { data: factorsData, isLoading: factorsLoading } = useEmissionFactors(listParams);
  const { data: transactionsData, isLoading: transactionsLoading } = useCarbonTransactions(listParams);
  const { data: goalsData, isLoading: goalsLoading } = useEnvironmentalGoals(listParams);
  const { data: productsData, isLoading: productsLoading } = useProductEsgProfiles(listParams);

  const factorMutations = useEmissionFactorMutations();
  const transactionMutations = useCarbonTransactionMutations();
  const goalMutations = useGoalMutations();
  const productMutations = useProductEsgMutations();

  const [factorDialogOpen, setFactorDialogOpen] = useState(false);
  const [transactionDialogOpen, setTransactionDialogOpen] = useState(false);
  const [goalDialogOpen, setGoalDialogOpen] = useState(false);
  const [productDialogOpen, setProductDialogOpen] = useState(false);
  const [editingFactor, setEditingFactor] = useState<EmissionFactor | null>(null);
  const [editingTransaction, setEditingTransaction] = useState<CarbonTransaction | null>(null);
  const [editingGoal, setEditingGoal] = useState<EnvironmentalGoal | null>(null);
  const [editingProduct, setEditingProduct] = useState<ProductEsgProfile | null>(null);

  const [factorForm, setFactorForm] = useState<EmissionFactorInput>({
    name: "",
    source_type: "",
    unit: "kg",
    co2_factor: "",
    description: "",
    status: "ACTIVE",
  });

  const [transactionForm, setTransactionForm] = useState<CarbonTransactionInput>({
    department_id: "",
    emission_factor_id: "",
    activity_name: "",
    quantity: "",
    unit: "kg",
    transaction_date: new Date().toISOString().slice(0, 10),
  });

  const [goalForm, setGoalForm] = useState<EnvironmentalGoalInput>({
    department_id: "",
    title: "",
    target_value: "",
    current_value: "0",
    deadline: "",
  });

  const [productForm, setProductForm] = useState<ProductEsgInput>({
    product_name: "",
    carbon_score: "",
    recyclability: "",
    supplier_score: "",
    notes: "",
    status: "ACTIVE",
  });

  function resetFactorForm() {
    setEditingFactor(null);
    setFactorForm({
      name: "",
      source_type: "",
      unit: "kg",
      co2_factor: "",
      description: "",
      status: "ACTIVE",
    });
  }

  function resetTransactionForm() {
    setEditingTransaction(null);
    setTransactionForm({
      department_id: departments[0]?.id ?? "",
      emission_factor_id: factorsData?.data[0]?.id ?? "",
      activity_name: "",
      quantity: "",
      unit: "kg",
      transaction_date: new Date().toISOString().slice(0, 10),
    });
  }

  function resetGoalForm() {
    setEditingGoal(null);
    setGoalForm({
      department_id: departments[0]?.id ?? "",
      title: "",
      target_value: "",
      current_value: "0",
      deadline: "",
    });
  }

  function resetProductForm() {
    setEditingProduct(null);
    setProductForm({
      product_name: "",
      carbon_score: "",
      recyclability: "",
      supplier_score: "",
      notes: "",
      status: "ACTIVE",
    });
  }

  async function handleFactorSubmit() {
    try {
      if (editingFactor) {
        await factorMutations.update.mutateAsync({ id: editingFactor.id, payload: factorForm });
        toast({ title: "Emission factor updated" });
      } else {
        await factorMutations.create.mutateAsync(factorForm);
        toast({ title: "Emission factor created" });
      }
      setFactorDialogOpen(false);
      resetFactorForm();
    } catch {
      toast({ title: "Failed to save emission factor", variant: "destructive" });
    }
  }

  async function handleTransactionSubmit() {
    try {
      if (editingTransaction) {
        await transactionMutations.update.mutateAsync({
          id: editingTransaction.id,
          payload: transactionForm,
        });
        toast({ title: "Carbon transaction updated" });
      } else {
        await transactionMutations.create.mutateAsync(transactionForm);
        toast({ title: "Carbon transaction created" });
      }
      setTransactionDialogOpen(false);
      resetTransactionForm();
    } catch {
      toast({ title: "Failed to save carbon transaction", variant: "destructive" });
    }
  }

  async function handleGoalSubmit() {
    try {
      if (editingGoal) {
        await goalMutations.update.mutateAsync({ id: editingGoal.id, payload: goalForm });
        toast({ title: "Goal updated" });
      } else {
        await goalMutations.create.mutateAsync(goalForm);
        toast({ title: "Goal created" });
      }
      setGoalDialogOpen(false);
      resetGoalForm();
    } catch {
      toast({ title: "Failed to save goal", variant: "destructive" });
    }
  }

  async function handleProductSubmit() {
    try {
      if (editingProduct) {
        await productMutations.update.mutateAsync({ id: editingProduct.id, payload: productForm });
        toast({ title: "Product ESG profile updated" });
      } else {
        await productMutations.create.mutateAsync(productForm);
        toast({ title: "Product ESG profile created" });
      }
      setProductDialogOpen(false);
      resetProductForm();
    } catch {
      toast({ title: "Failed to save product ESG profile", variant: "destructive" });
    }
  }

  if (analyticsLoading) {
    return (
      <div className="space-y-4 p-6">
        <LoadingSkeleton className="h-10 w-64" />
        <LoadingSkeleton className="h-48 w-full" />
      </div>
    );
  }

  if (isError || !analytics) {
    return (
      <div className="p-6">
        <ErrorState
          title="Unable to load environmental data"
          message="Please try again later."
          onRetry={() => void refetch()}
        />
      </div>
    );
  }

  return (
    <div className="space-y-8 p-4 md:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Leaf className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold tracking-tight">Environmental Dashboard</h1>
          </div>
          <p className="text-sm text-muted-foreground">
            Track carbon emissions, goals, and product ESG performance
          </p>
        </div>
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            className="pl-9"
            placeholder="Search across tables..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Emissions</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{formatNumber(analytics.total_emissions)} kg CO₂</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Goals</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{analytics.active_goals}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Completed Goals</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{analytics.completed_goals}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Departments Tracked</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{analytics.department_carbon_totals.length}</p>
          </CardContent>
        </Card>
      </div>

      <EnvironmentalCharts analytics={analytics} />

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Environmental Goals</h2>
          {canWrite ? (
            <Button
              size="sm"
              onClick={() => {
                resetGoalForm();
                setGoalDialogOpen(true);
              }}
            >
              <Plus className="mr-1 h-4 w-4" />
              Add Goal
            </Button>
          ) : null}
        </div>
        {goalsLoading ? (
          <LoadingSkeleton className="h-32 w-full" />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {(goalsData?.data ?? []).map((goal) => (
              <Card key={goal.id} className="overflow-hidden">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-base">{goal.title}</CardTitle>
                    <Badge variant={goalStatusVariant(goal.status)}>{goal.status}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{goal.department_name}</p>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <div className="mb-1 flex justify-between text-xs">
                      <span>Progress</span>
                      <span>{formatNumber(goal.progress_percentage, 0)}%</span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary transition-all"
                        style={{ width: `${Math.min(Number(goal.progress_percentage), 100)}%` }}
                      />
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {formatNumber(goal.current_value)} / {formatNumber(goal.target_value)} · Due{" "}
                    {goal.deadline}
                  </p>
                  {canWrite ? (
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setEditingGoal(goal);
                          setGoalForm({
                            department_id: goal.department_id,
                            title: goal.title,
                            target_value: goal.target_value,
                            current_value: goal.current_value,
                            deadline: goal.deadline,
                          });
                          setGoalDialogOpen(true);
                        }}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={async () => {
                          try {
                            await goalMutations.remove.mutateAsync(goal.id);
                            toast({ title: "Goal deleted" });
                          } catch {
                            toast({ title: "Failed to delete goal", variant: "destructive" });
                          }
                        }}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : null}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </section>

      <section className="rounded-lg border bg-card shadow-sm">
        <div className="flex items-center justify-between border-b p-4">
          <h2 className="text-lg font-semibold">Emission Factors</h2>
          {canWrite ? (
            <Button
              size="sm"
              onClick={() => {
                resetFactorForm();
                setFactorDialogOpen(true);
              }}
            >
              <Plus className="mr-1 h-4 w-4" />
              Add Factor
            </Button>
          ) : null}
        </div>
        {factorsLoading ? (
          <div className="p-4">
            <LoadingSkeleton className="h-32 w-full" />
          </div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Source Type</TableHead>
                  <TableHead>Unit</TableHead>
                  <TableHead>CO₂ Factor</TableHead>
                  <TableHead>Status</TableHead>
                  {canWrite ? <TableHead className="text-right">Actions</TableHead> : null}
                </TableRow>
              </TableHeader>
              <TableBody>
                {(factorsData?.data ?? []).map((factor) => (
                  <TableRow key={factor.id}>
                    <TableCell className="font-medium">{factor.name}</TableCell>
                    <TableCell>{factor.source_type}</TableCell>
                    <TableCell>{factor.unit}</TableCell>
                    <TableCell>{formatNumber(factor.co2_factor, 4)}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{factor.status}</Badge>
                    </TableCell>
                    {canWrite ? (
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingFactor(factor);
                              setFactorForm({
                                name: factor.name,
                                source_type: factor.source_type,
                                unit: factor.unit,
                                co2_factor: factor.co2_factor,
                                description: factor.description ?? "",
                                status: factor.status,
                              });
                              setFactorDialogOpen(true);
                            }}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={async () => {
                              try {
                                await factorMutations.remove.mutateAsync(factor.id);
                                toast({ title: "Emission factor deleted" });
                              } catch {
                                toast({
                                  title: "Failed to delete emission factor",
                                  variant: "destructive",
                                });
                              }
                            }}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    ) : null}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {factorsData?.pagination ? (
              <PaginationBar
                page={factorsData.pagination.page}
                pages={factorsData.pagination.pages}
                total={factorsData.pagination.total}
                onPageChange={setPage}
              />
            ) : null}
          </>
        )}
      </section>

      <section className="rounded-lg border bg-card shadow-sm">
        <div className="flex items-center justify-between border-b p-4">
          <h2 className="text-lg font-semibold">Carbon Transactions</h2>
          {canWrite ? (
            <Button
              size="sm"
              onClick={() => {
                resetTransactionForm();
                setTransactionDialogOpen(true);
              }}
            >
              <Plus className="mr-1 h-4 w-4" />
              Add Transaction
            </Button>
          ) : null}
        </div>
        {transactionsLoading ? (
          <div className="p-4">
            <LoadingSkeleton className="h-32 w-full" />
          </div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Activity</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Factor</TableHead>
                  <TableHead>Quantity</TableHead>
                  <TableHead>Calculated CO₂</TableHead>
                  <TableHead>Date</TableHead>
                  {canWrite ? <TableHead className="text-right">Actions</TableHead> : null}
                </TableRow>
              </TableHeader>
              <TableBody>
                {(transactionsData?.data ?? []).map((tx) => (
                  <TableRow key={tx.id}>
                    <TableCell className="font-medium">{tx.activity_name}</TableCell>
                    <TableCell>{tx.department_name}</TableCell>
                    <TableCell>{tx.emission_factor_name}</TableCell>
                    <TableCell>
                      {formatNumber(tx.quantity, 2)} {tx.unit}
                    </TableCell>
                    <TableCell>{formatNumber(tx.calculated_emission, 4)} kg</TableCell>
                    <TableCell>{tx.transaction_date}</TableCell>
                    {canWrite ? (
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingTransaction(tx);
                              setTransactionForm({
                                department_id: tx.department_id,
                                emission_factor_id: tx.emission_factor_id,
                                activity_name: tx.activity_name,
                                quantity: tx.quantity,
                                unit: tx.unit,
                                transaction_date: tx.transaction_date,
                              });
                              setTransactionDialogOpen(true);
                            }}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={async () => {
                              try {
                                await transactionMutations.remove.mutateAsync(tx.id);
                                toast({ title: "Transaction deleted" });
                              } catch {
                                toast({
                                  title: "Failed to delete transaction",
                                  variant: "destructive",
                                });
                              }
                            }}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    ) : null}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {transactionsData?.pagination ? (
              <PaginationBar
                page={transactionsData.pagination.page}
                pages={transactionsData.pagination.pages}
                total={transactionsData.pagination.total}
                onPageChange={setPage}
              />
            ) : null}
          </>
        )}
      </section>

      <section className="rounded-lg border bg-card shadow-sm">
        <div className="flex items-center justify-between border-b p-4">
          <h2 className="text-lg font-semibold">Product ESG Profiles</h2>
          {canWrite ? (
            <Button
              size="sm"
              onClick={() => {
                resetProductForm();
                setProductDialogOpen(true);
              }}
            >
              <Plus className="mr-1 h-4 w-4" />
              Add Product
            </Button>
          ) : null}
        </div>
        {productsLoading ? (
          <div className="p-4">
            <LoadingSkeleton className="h-32 w-full" />
          </div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Product</TableHead>
                  <TableHead>Carbon Score</TableHead>
                  <TableHead>Recyclability</TableHead>
                  <TableHead>Supplier Score</TableHead>
                  <TableHead>Status</TableHead>
                  {canWrite ? <TableHead className="text-right">Actions</TableHead> : null}
                </TableRow>
              </TableHeader>
              <TableBody>
                {(productsData?.data ?? []).map((product) => (
                  <TableRow key={product.id}>
                    <TableCell className="font-medium">{product.product_name}</TableCell>
                    <TableCell>{formatNumber(product.carbon_score)}</TableCell>
                    <TableCell>{formatNumber(product.recyclability)}%</TableCell>
                    <TableCell>{formatNumber(product.supplier_score)}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{product.status}</Badge>
                    </TableCell>
                    {canWrite ? (
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingProduct(product);
                              setProductForm({
                                product_name: product.product_name,
                                carbon_score: product.carbon_score,
                                recyclability: product.recyclability,
                                supplier_score: product.supplier_score,
                                notes: product.notes ?? "",
                                status: product.status,
                              });
                              setProductDialogOpen(true);
                            }}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={async () => {
                              try {
                                await productMutations.remove.mutateAsync(product.id);
                                toast({ title: "Product deleted" });
                              } catch {
                                toast({ title: "Failed to delete product", variant: "destructive" });
                              }
                            }}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    ) : null}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {productsData?.pagination ? (
              <PaginationBar
                page={productsData.pagination.page}
                pages={productsData.pagination.pages}
                total={productsData.pagination.total}
                onPageChange={setPage}
              />
            ) : null}
          </>
        )}
      </section>

      <Dialog open={factorDialogOpen} onOpenChange={setFactorDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingFactor ? "Edit Emission Factor" : "Add Emission Factor"}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="factor-name">Name</Label>
              <Input
                id="factor-name"
                value={factorForm.name}
                onChange={(e) => setFactorForm({ ...factorForm, name: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="factor-source">Source Type</Label>
              <Input
                id="factor-source"
                value={factorForm.source_type}
                onChange={(e) => setFactorForm({ ...factorForm, source_type: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="factor-unit">Unit</Label>
                <Input
                  id="factor-unit"
                  value={factorForm.unit}
                  onChange={(e) => setFactorForm({ ...factorForm, unit: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="factor-co2">CO₂ Factor</Label>
                <Input
                  id="factor-co2"
                  type="number"
                  step="0.0001"
                  min="0.0001"
                  value={factorForm.co2_factor}
                  onChange={(e) => setFactorForm({ ...factorForm, co2_factor: e.target.value })}
                />
              </div>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="factor-desc">Description</Label>
              <Textarea
                id="factor-desc"
                value={factorForm.description}
                onChange={(e) => setFactorForm({ ...factorForm, description: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setFactorDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handleFactorSubmit()}>
              {editingFactor ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={transactionDialogOpen} onOpenChange={setTransactionDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingTransaction ? "Edit Carbon Transaction" : "Add Carbon Transaction"}
            </DialogTitle>
          </DialogHeader>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label>Department</Label>
              <Select
                value={transactionForm.department_id}
                onChange={(e) =>
                  setTransactionForm({ ...transactionForm, department_id: e.target.value })
                }
              >
                <option value="">Select department</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name}
                  </option>
                ))}
              </Select>
            </div>
            <div className="grid gap-2">
              <Label>Emission Factor</Label>
              <Select
                value={transactionForm.emission_factor_id}
                onChange={(e) =>
                  setTransactionForm({ ...transactionForm, emission_factor_id: e.target.value })
                }
              >
                <option value="">Select factor</option>
                {(factorsData?.data ?? []).map((factor) => (
                  <option key={factor.id} value={factor.id}>
                    {factor.name} ({factor.co2_factor} {factor.unit})
                  </option>
                ))}
              </Select>
            </div>
            <div className="grid gap-2">
              <Label>Activity Name</Label>
              <Input
                value={transactionForm.activity_name}
                onChange={(e) =>
                  setTransactionForm({ ...transactionForm, activity_name: e.target.value })
                }
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label>Quantity</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={transactionForm.quantity}
                  onChange={(e) =>
                    setTransactionForm({ ...transactionForm, quantity: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-2">
                <Label>Unit</Label>
                <Input
                  value={transactionForm.unit}
                  onChange={(e) => setTransactionForm({ ...transactionForm, unit: e.target.value })}
                />
              </div>
            </div>
            <div className="grid gap-2">
              <Label>Transaction Date</Label>
              <Input
                type="date"
                value={transactionForm.transaction_date}
                onChange={(e) =>
                  setTransactionForm({ ...transactionForm, transaction_date: e.target.value })
                }
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setTransactionDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handleTransactionSubmit()}>
              {editingTransaction ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={goalDialogOpen} onOpenChange={setGoalDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingGoal ? "Edit Goal" : "Add Environmental Goal"}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label>Title</Label>
              <Input
                value={goalForm.title}
                onChange={(e) => setGoalForm({ ...goalForm, title: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label>Department</Label>
              <Select
                value={goalForm.department_id}
                onChange={(e) => setGoalForm({ ...goalForm, department_id: e.target.value })}
              >
                <option value="">Select department</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name}
                  </option>
                ))}
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label>Target Value</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={goalForm.target_value}
                  onChange={(e) => setGoalForm({ ...goalForm, target_value: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label>Current Value</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={goalForm.current_value}
                  onChange={(e) => setGoalForm({ ...goalForm, current_value: e.target.value })}
                />
              </div>
            </div>
            <div className="grid gap-2">
              <Label>Deadline</Label>
              <Input
                type="date"
                value={goalForm.deadline}
                onChange={(e) => setGoalForm({ ...goalForm, deadline: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setGoalDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handleGoalSubmit()}>{editingGoal ? "Update" : "Create"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={productDialogOpen} onOpenChange={setProductDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingProduct ? "Edit Product ESG Profile" : "Add Product ESG Profile"}
            </DialogTitle>
          </DialogHeader>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label>Product Name</Label>
              <Input
                value={productForm.product_name}
                onChange={(e) => setProductForm({ ...productForm, product_name: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="grid gap-2">
                <Label>Carbon Score</Label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  value={productForm.carbon_score}
                  onChange={(e) => setProductForm({ ...productForm, carbon_score: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label>Recyclability %</Label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  value={productForm.recyclability}
                  onChange={(e) => setProductForm({ ...productForm, recyclability: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label>Supplier Score</Label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  value={productForm.supplier_score}
                  onChange={(e) =>
                    setProductForm({ ...productForm, supplier_score: e.target.value })
                  }
                />
              </div>
            </div>
            <div className="grid gap-2">
              <Label>Notes</Label>
              <Textarea
                value={productForm.notes}
                onChange={(e) => setProductForm({ ...productForm, notes: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setProductDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handleProductSubmit()}>
              {editingProduct ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
