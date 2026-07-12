import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Check, HandHeart, Plus, Search, Trash2, X } from "lucide-react";

import { usePermission } from "@/modules/auth/hooks/usePermission";
import { SocialCharts } from "@/modules/social/components/SocialCharts";
import {
  useCsrActivities,
  useCsrActivityMutations,
  useParticipationMutations,
  useParticipations,
  useSocialAnalytics,
  useSocialDepartments,
} from "@/modules/social/hooks/useSocial";
import type { CsrActivity, CsrActivityInput, Participation } from "@/modules/social/types/social.types";
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
import { EmptyState, ErrorState, LoadingSkeleton, TableSkeleton } from "@/shared/components/feedback/states";
import { PageHeader } from "@/shared/components/layout/PageHeader";
import { PaginationBar } from "@/shared/components/layout/PaginationBar";
import { useToast } from "@/shared/hooks/use-toast";

function approvalVariant(status: string): "default" | "secondary" | "destructive" {
  if (status === "APPROVED") return "default";
  if (status === "REJECTED") return "destructive";
  return "secondary";
}

export function SocialPage() {
  const canWrite = usePermission("csr:write");
  const canParticipate = usePermission("csr:participate");
  const { toast } = useToast();

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [approvalFilter, setApprovalFilter] = useState("");
  const listParams = useMemo(
    () => ({
      page,
      page_size: 10,
      search: search || undefined,
      approval_status: approvalFilter || undefined,
    }),
    [page, search, approvalFilter],
  );

  const { data: departments = [] } = useSocialDepartments();
  const { data: analytics, isLoading: analyticsLoading, isError, refetch } = useSocialAnalytics();
  const { data: activitiesData, isLoading: activitiesLoading } = useCsrActivities(listParams);
  const { data: participationsData, isLoading: participationsLoading } = useParticipations(listParams);

  const activityMutations = useCsrActivityMutations();
  const participationMutations = useParticipationMutations();

  const [activityDialogOpen, setActivityDialogOpen] = useState(false);
  const [participationDialogOpen, setParticipationDialogOpen] = useState(false);
  const [editingActivity, setEditingActivity] = useState<CsrActivity | null>(null);

  const [activityForm, setActivityForm] = useState<CsrActivityInput>({
    title: "",
    category: "",
    department_id: "",
    description: "",
    start_date: new Date().toISOString().slice(0, 10),
    end_date: "",
    points: 10,
    evidence_required: false,
    status: "ACTIVE",
  });

  const [participationForm, setParticipationForm] = useState({
    csr_activity_id: "",
    proof_file: "",
  });

  function resetActivityForm() {
    setEditingActivity(null);
    setActivityForm({
      title: "",
      category: "",
      department_id: departments[0]?.id ?? "",
      description: "",
      start_date: new Date().toISOString().slice(0, 10),
      end_date: "",
      points: 10,
      evidence_required: false,
      status: "ACTIVE",
    });
  }

  async function handleActivitySubmit() {
    try {
      if (editingActivity) {
        await activityMutations.update.mutateAsync({ id: editingActivity.id, payload: activityForm });
        toast({ title: "CSR activity updated" });
      } else {
        await activityMutations.create.mutateAsync(activityForm);
        toast({ title: "CSR activity created" });
      }
      setActivityDialogOpen(false);
      resetActivityForm();
    } catch {
      toast({ title: "Failed to save CSR activity", variant: "destructive" });
    }
  }

  async function handleParticipationSubmit() {
    try {
      await participationMutations.create.mutateAsync(participationForm);
      toast({ title: "Participation submitted" });
      setParticipationDialogOpen(false);
      setParticipationForm({ csr_activity_id: "", proof_file: "" });
    } catch {
      toast({ title: "Failed to join activity", variant: "destructive" });
    }
  }

  if (analyticsLoading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton className="h-10 w-64" />
        <LoadingSkeleton className="h-48 w-full rounded-xl" />
      </div>
    );
  }

  if (isError || !analytics) {
    return (
      <ErrorState
        title="Unable to load social data"
        message="The CSR dashboard could not be loaded."
        onRetry={() => void refetch()}
      />
    );
  }

  const pendingApprovals = participationsData?.data.filter((p) => p.approval_status === "PENDING") ?? [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="space-y-8"
    >
      <PageHeader
        icon={HandHeart}
        title="CSR Dashboard"
        description="Manage CSR activities, participation, and social impact metrics"
        action={
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              className="pl-9"
              placeholder="Search activities..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              aria-label="Search CSR activities"
            />
          </div>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Social Score</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{Number(analytics.social_score).toFixed(1)}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Participation Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{Number(analytics.participation_rate).toFixed(1)}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Activities</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{analytics.active_csr_activities}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Pending Approvals</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{analytics.pending_approvals}</p>
          </CardContent>
        </Card>
      </div>

      <SocialCharts analytics={analytics} />

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {activitiesData?.data.slice(0, 3).map((activity) => (
          <Card key={activity.id}>
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between gap-2">
                <CardTitle className="text-base">{activity.title}</CardTitle>
                <Badge variant="secondary">{activity.status}</Badge>
              </div>
              <p className="text-xs text-muted-foreground">{activity.department_name}</p>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>{activity.category}</p>
              <p className="text-muted-foreground">
                {activity.approved_count}/{activity.participation_count} approved · {activity.points} pts
              </p>
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-primary"
                  style={{
                    width: `${
                      activity.participation_count > 0
                        ? (activity.approved_count / activity.participation_count) * 100
                        : 0
                    }%`,
                  }}
                />
              </div>
            </CardContent>
          </Card>
        ))}
      </section>

      {canWrite ? (
        <section className="rounded-xl border bg-card shadow-sm transition-shadow hover:shadow-md">
          <div className="flex items-center justify-between border-b p-4">
            <h2 className="text-lg font-semibold">Approval Queue</h2>
            <Badge>{pendingApprovals.length} pending</Badge>
          </div>
          {participationsLoading ? (
            <div className="p-4">
              <LoadingSkeleton className="h-24 w-full" />
            </div>
          ) : pendingApprovals.length === 0 ? (
            <div className="p-4">
              <EmptyState title="No pending approvals" description="All participation requests are processed." />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Activity</TableHead>
                  <TableHead>Proof</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pendingApprovals.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.employee_name}</TableCell>
                    <TableCell>{item.csr_activity_title}</TableCell>
                    <TableCell className="max-w-[200px] truncate">{item.proof_file ?? "—"}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          size="sm"
                          onClick={async () => {
                            try {
                              await participationMutations.approve.mutateAsync(item.id);
                              toast({ title: "Participation approved" });
                            } catch {
                              toast({ title: "Approval failed", variant: "destructive" });
                            }
                          }}
                        >
                          <Check className="mr-1 h-4 w-4" />
                          Approve
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={async () => {
                            try {
                              await participationMutations.reject.mutateAsync({ id: item.id });
                              toast({ title: "Participation rejected" });
                            } catch {
                              toast({ title: "Rejection failed", variant: "destructive" });
                            }
                          }}
                        >
                          <X className="mr-1 h-4 w-4" />
                          Reject
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </section>
      ) : null}

      <section className="rounded-xl border bg-card shadow-sm transition-shadow hover:shadow-md">
        <div className="flex items-center justify-between border-b p-4">
          <h2 className="text-lg font-semibold">CSR Activities</h2>
          <div className="flex gap-2">
            {canParticipate ? (
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setParticipationForm({
                    csr_activity_id: activitiesData?.data[0]?.id ?? "",
                    proof_file: "",
                  });
                  setParticipationDialogOpen(true);
                }}
              >
                Join Activity
              </Button>
            ) : null}
            {canWrite ? (
              <Button
                size="sm"
                onClick={() => {
                  resetActivityForm();
                  setActivityDialogOpen(true);
                }}
              >
                <Plus className="mr-1 h-4 w-4" />
                Add Activity
              </Button>
            ) : null}
          </div>
        </div>
        {activitiesLoading ? (
          <div className="p-4">
            <TableSkeleton rows={5} columns={5} />
          </div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Points</TableHead>
                  <TableHead>Status</TableHead>
                  {canWrite ? <TableHead className="text-right">Actions</TableHead> : null}
                </TableRow>
              </TableHeader>
              <TableBody>
                {(activitiesData?.data ?? []).map((activity) => (
                  <TableRow key={activity.id}>
                    <TableCell className="font-medium">{activity.title}</TableCell>
                    <TableCell>{activity.category}</TableCell>
                    <TableCell>{activity.department_name}</TableCell>
                    <TableCell>{activity.points}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{activity.status}</Badge>
                    </TableCell>
                    {canWrite ? (
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setEditingActivity(activity);
                              setActivityForm({
                                title: activity.title,
                                category: activity.category,
                                department_id: activity.department_id,
                                description: activity.description ?? "",
                                start_date: activity.start_date,
                                end_date: activity.end_date,
                                points: activity.points,
                                evidence_required: activity.evidence_required,
                                status: activity.status,
                              });
                              setActivityDialogOpen(true);
                            }}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={async () => {
                              try {
                                await activityMutations.remove.mutateAsync(activity.id);
                                toast({ title: "Activity deleted" });
                              } catch {
                                toast({ title: "Delete failed", variant: "destructive" });
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
            {activitiesData?.pagination ? (
              <PaginationBar
                page={activitiesData.pagination.page}
                pages={activitiesData.pagination.pages}
                total={activitiesData.pagination.total}
                onPageChange={setPage}
              />
            ) : null}
          </>
        )}
      </section>

      <section className="rounded-xl border bg-card shadow-sm transition-shadow hover:shadow-md">
        <div className="flex items-center justify-between border-b p-4">
          <h2 className="text-lg font-semibold">Participation Records</h2>
          <Select
            value={approvalFilter}
            onChange={(e) => {
              setApprovalFilter(e.target.value);
              setPage(1);
            }}
            className="w-40"
          >
            <option value="">All statuses</option>
            <option value="PENDING">Pending</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
          </Select>
        </div>
        {participationsLoading ? (
          <div className="p-4">
            <TableSkeleton rows={5} columns={5} />
          </div>
        ) : (participationsData?.data ?? []).length === 0 ? (
          <div className="p-4">
            <EmptyState title="No participations" description="Employee participations will appear here." />
          </div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Activity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Points</TableHead>
                  <TableHead>Completion</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(participationsData?.data ?? []).map((item: Participation) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.employee_name}</TableCell>
                    <TableCell>{item.csr_activity_title}</TableCell>
                    <TableCell>
                      <Badge variant={approvalVariant(item.approval_status)}>
                        {item.approval_status}
                      </Badge>
                    </TableCell>
                    <TableCell>{item.points_earned}</TableCell>
                    <TableCell>{item.completion_date ?? "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {participationsData?.pagination ? (
              <PaginationBar
                page={participationsData.pagination.page}
                pages={participationsData.pagination.pages}
                total={participationsData.pagination.total}
                onPageChange={setPage}
              />
            ) : null}
          </>
        )}
      </section>

      <section className="rounded-xl border bg-card shadow-sm transition-shadow hover:shadow-md">
        <div className="border-b p-4">
          <h2 className="text-lg font-semibold">Department Leaderboard</h2>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Department</TableHead>
              <TableHead>Participations</TableHead>
              <TableHead>Approved</TableHead>
              <TableHead>Rate</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {analytics.department_participation.map((dept) => (
              <TableRow key={dept.department_id}>
                <TableCell className="font-medium">{dept.department_name}</TableCell>
                <TableCell>{dept.participation_count}</TableCell>
                <TableCell>{dept.approved_count}</TableCell>
                <TableCell>{Number(dept.participation_rate).toFixed(1)}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </section>

      <Dialog open={activityDialogOpen} onOpenChange={setActivityDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingActivity ? "Edit CSR Activity" : "Add CSR Activity"}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label>Title</Label>
              <Input
                value={activityForm.title}
                onChange={(e) => setActivityForm({ ...activityForm, title: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label>Category</Label>
                <Input
                  value={activityForm.category}
                  onChange={(e) => setActivityForm({ ...activityForm, category: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label>Points</Label>
                <Input
                  type="number"
                  min="0"
                  value={activityForm.points}
                  onChange={(e) =>
                    setActivityForm({ ...activityForm, points: Number(e.target.value) })
                  }
                />
              </div>
            </div>
            <div className="grid gap-2">
              <Label>Department</Label>
              <Select
                value={activityForm.department_id}
                onChange={(e) =>
                  setActivityForm({ ...activityForm, department_id: e.target.value })
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
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label>Start Date</Label>
                <Input
                  type="date"
                  value={activityForm.start_date}
                  onChange={(e) =>
                    setActivityForm({ ...activityForm, start_date: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-2">
                <Label>End Date</Label>
                <Input
                  type="date"
                  value={activityForm.end_date}
                  onChange={(e) => setActivityForm({ ...activityForm, end_date: e.target.value })}
                />
              </div>
            </div>
            <div className="grid gap-2">
              <Label>Description</Label>
              <Textarea
                value={activityForm.description}
                onChange={(e) =>
                  setActivityForm({ ...activityForm, description: e.target.value })
                }
              />
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={activityForm.evidence_required}
                onChange={(e) =>
                  setActivityForm({ ...activityForm, evidence_required: e.target.checked })
                }
              />
              Evidence required for approval
            </label>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setActivityDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handleActivitySubmit()}>
              {editingActivity ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={participationDialogOpen} onOpenChange={setParticipationDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Join CSR Activity</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label>CSR Activity</Label>
              <Select
                value={participationForm.csr_activity_id}
                onChange={(e) =>
                  setParticipationForm({ ...participationForm, csr_activity_id: e.target.value })
                }
              >
                <option value="">Select activity</option>
                {(activitiesData?.data ?? [])
                  .filter((a) => a.status === "ACTIVE")
                  .map((activity) => (
                    <option key={activity.id} value={activity.id}>
                      {activity.title}
                    </option>
                  ))}
              </Select>
            </div>
            <div className="grid gap-2">
              <Label>Proof File URL</Label>
              <Input
                value={participationForm.proof_file}
                onChange={(e) =>
                  setParticipationForm({ ...participationForm, proof_file: e.target.value })
                }
                placeholder="https://storage.example.com/proof.jpg"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setParticipationDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handleParticipationSubmit()}>Submit Participation</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}
