import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  FileText,
  Plus,
  Scale,
  Search,
  Shield,
  Trash2,
} from "lucide-react";

import { usePermission } from "@/modules/auth/hooks/usePermission";
import { GovernanceCharts } from "@/modules/governance/components/GovernanceCharts";
import {
  useAudits,
  useAuditMutations,
  useComplianceIssueMutations,
  useComplianceIssues,
  useGovernanceAnalytics,
  useGovernanceDepartments,
  useGovernanceEmployees,
  usePolicies,
  usePolicyMutations,
} from "@/modules/governance/hooks/useGovernance";
import type {
  AuditInput,
  ComplianceIssue,
  ComplianceIssueInput,
  Policy,
  PolicyInput,
} from "@/modules/governance/types/governance.types";
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
import { EmptyState, ErrorState, LoadingSkeleton } from "@/shared/components/feedback/states";
import { useToast } from "@/shared/hooks/use-toast";

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
        <Button variant="outline" size="sm" disabled={page >= pages} onClick={() => onPageChange(page + 1)}>
          Next
        </Button>
      </div>
    </div>
  );
}

function severityVariant(severity: string): "default" | "secondary" | "destructive" {
  if (severity === "CRITICAL" || severity === "HIGH") return "destructive";
  if (severity === "MEDIUM") return "default";
  return "secondary";
}

function issueStatusVariant(status: string): "default" | "secondary" | "destructive" {
  if (status === "OVERDUE") return "destructive";
  if (status === "CLOSED") return "default";
  return "secondary";
}

export function GovernancePage() {
  const canWritePolicies = usePermission("policies:write");
  const canAcknowledge = usePermission("policies:acknowledge");
  const canWriteAudits = usePermission("audits:write");
  const { toast } = useToast();

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [issueFilter, setIssueFilter] = useState("");
  const listParams = useMemo(
    () => ({
      page,
      page_size: 10,
      search: search || undefined,
      status: issueFilter || undefined,
    }),
    [page, search, issueFilter],
  );

  const { data: departments = [] } = useGovernanceDepartments();
  const { data: employees = [] } = useGovernanceEmployees();
  const { data: analytics, isLoading: analyticsLoading, isError, refetch } = useGovernanceAnalytics();
  const { data: policiesData, isLoading: policiesLoading } = usePolicies(listParams);
  const { data: auditsData, isLoading: auditsLoading } = useAudits(listParams);
  const { data: issuesData, isLoading: issuesLoading } = useComplianceIssues(listParams);

  const policyMutations = usePolicyMutations();
  const auditMutations = useAuditMutations();
  const issueMutations = useComplianceIssueMutations();

  const [policyDialogOpen, setPolicyDialogOpen] = useState(false);
  const [auditDialogOpen, setAuditDialogOpen] = useState(false);
  const [issueDialogOpen, setIssueDialogOpen] = useState(false);

  const [policyForm, setPolicyForm] = useState<PolicyInput>({
    title: "",
    version: "1.0",
    description: "",
    effective_date: new Date().toISOString().slice(0, 10),
    status: "ACTIVE",
  });

  const [auditForm, setAuditForm] = useState<AuditInput>({
    department_id: "",
    title: "",
    auditor_id: "",
    audit_date: new Date().toISOString().slice(0, 10),
    status: "PLANNED",
  });

  const [issueForm, setIssueForm] = useState<ComplianceIssueInput>({
    owner_id: "",
    severity: "MEDIUM",
    description: "",
    due_date: new Date().toISOString().slice(0, 10),
  });

  const kpiCards = analytics
    ? [
        {
          title: "Governance Score",
          value: `${Number(analytics.governance_score).toFixed(1)}%`,
          icon: Scale,
          description: "Composite policy, compliance, and audit score",
        },
        {
          title: "Compliance Rate",
          value: `${Number(analytics.compliance_rate).toFixed(1)}%`,
          icon: Shield,
          description: "Closed issues vs total issues",
        },
        {
          title: "Open Issues",
          value: String(analytics.open_issues),
          icon: AlertTriangle,
          description: "Active compliance issues requiring action",
        },
        {
          title: "Policy Completion",
          value: `${Number(analytics.policy_completion).toFixed(1)}%`,
          icon: ClipboardCheck,
          description: "Employee policy acknowledgement rate",
        },
      ]
    : [];

  async function handleCreatePolicy() {
    try {
      await policyMutations.create.mutateAsync(policyForm);
      setPolicyDialogOpen(false);
      toast({ title: "Policy created" });
    } catch {
      toast({ title: "Failed to create policy", variant: "destructive" });
    }
  }

  async function handleCreateAudit() {
    try {
      await auditMutations.create.mutateAsync(auditForm);
      setAuditDialogOpen(false);
      toast({ title: "Audit created" });
    } catch {
      toast({ title: "Failed to create audit", variant: "destructive" });
    }
  }

  async function handleCreateIssue() {
    try {
      await issueMutations.create.mutateAsync(issueForm);
      setIssueDialogOpen(false);
      toast({ title: "Compliance issue created" });
    } catch {
      toast({ title: "Failed to create issue", variant: "destructive" });
    }
  }

  async function handleAcknowledgePolicy(policy: Policy) {
    try {
      await policyMutations.acknowledge.mutateAsync(policy.id);
      toast({ title: "Policy acknowledged" });
    } catch {
      toast({ title: "Failed to acknowledge policy", variant: "destructive" });
    }
  }

  async function handleCloseIssue(issue: ComplianceIssue) {
    try {
      await issueMutations.close.mutateAsync(issue.id);
      toast({ title: "Issue closed" });
    } catch {
      toast({ title: "Failed to close issue", variant: "destructive" });
    }
  }

  if (isError) {
    return (
      <ErrorState
        title="Failed to load governance dashboard"
        message="Could not retrieve governance analytics."
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold tracking-tight">Governance Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Policies, audits, compliance tracking, and governance performance
        </p>
      </motion.div>

      {analyticsLoading ? (
        <LoadingSkeleton className="h-28 w-full" />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {kpiCards.map((card, index) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {card.title}
                  </CardTitle>
                  <card.icon className="h-4 w-4 text-primary" />
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{card.value}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{card.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {analytics && <GovernanceCharts analytics={analytics} />}

      <Card>
        <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <FileText className="h-4 w-4" />
            Policy Table
          </CardTitle>
          <div className="flex flex-wrap gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                className="pl-8"
                placeholder="Search policies..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
              />
            </div>
            {canWritePolicies && (
              <Button size="sm" onClick={() => setPolicyDialogOpen(true)}>
                <Plus className="mr-1 h-4 w-4" />
                Add Policy
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {policiesLoading ? (
            <LoadingSkeleton className="m-4 h-40" />
          ) : !policiesData?.data.length ? (
            <EmptyState title="No policies" description="Create a policy to get started." />
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Title</TableHead>
                    <TableHead>Version</TableHead>
                    <TableHead>Effective Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Acknowledgements</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {policiesData.data.map((policy) => (
                    <TableRow key={policy.id}>
                      <TableCell className="font-medium">{policy.title}</TableCell>
                      <TableCell>{policy.version}</TableCell>
                      <TableCell>{policy.effective_date}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{policy.status}</Badge>
                      </TableCell>
                      <TableCell>{policy.acknowledgement_count}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          {canAcknowledge && policy.status === "ACTIVE" && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => void handleAcknowledgePolicy(policy)}
                            >
                              <CheckCircle2 className="mr-1 h-3 w-3" />
                              Acknowledge
                            </Button>
                          )}
                          {canWritePolicies && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() =>
                                void policyMutations.remove.mutateAsync(policy.id).then(() =>
                                  toast({ title: "Policy deleted" }),
                                )
                              }
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <PaginationBar
                page={policiesData.pagination.page}
                pages={policiesData.pagination.pages}
                total={policiesData.pagination.total}
                onPageChange={setPage}
              />
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <ClipboardCheck className="h-4 w-4" />
            Audit Table
          </CardTitle>
          {canWriteAudits && (
            <Button size="sm" onClick={() => setAuditDialogOpen(true)}>
              <Plus className="mr-1 h-4 w-4" />
              Add Audit
            </Button>
          )}
        </CardHeader>
        <CardContent className="p-0">
          {auditsLoading ? (
            <LoadingSkeleton className="m-4 h-40" />
          ) : !auditsData?.data.length ? (
            <EmptyState title="No audits" description="Schedule an audit to begin tracking." />
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Title</TableHead>
                    <TableHead>Department</TableHead>
                    <TableHead>Auditor</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Issues</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {auditsData.data.map((audit) => (
                    <TableRow key={audit.id}>
                      <TableCell className="font-medium">{audit.title}</TableCell>
                      <TableCell>{audit.department_name ?? "—"}</TableCell>
                      <TableCell>{audit.auditor_name ?? "—"}</TableCell>
                      <TableCell>{audit.audit_date}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{audit.status}</Badge>
                      </TableCell>
                      <TableCell>
                        {audit.open_issue_count}/{audit.issue_count}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <PaginationBar
                page={auditsData.pagination.page}
                pages={auditsData.pagination.pages}
                total={auditsData.pagination.total}
                onPageChange={setPage}
              />
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <AlertTriangle className="h-4 w-4" />
            Compliance Issue Tracker
          </CardTitle>
          <div className="flex flex-wrap gap-2">
            <Select
              value={issueFilter}
              onChange={(e) => {
                setIssueFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All statuses</option>
              <option value="OPEN">Open</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="OVERDUE">Overdue</option>
              <option value="CLOSED">Closed</option>
            </Select>
            {canWriteAudits && (
              <Button size="sm" onClick={() => setIssueDialogOpen(true)}>
                <Plus className="mr-1 h-4 w-4" />
                Raise Issue
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {issuesLoading ? (
            <LoadingSkeleton className="m-4 h-40" />
          ) : !issuesData?.data.length ? (
            <EmptyState title="No compliance issues" description="All issues are resolved." />
          ) : (
            <>
              <div className="grid gap-3 p-4 md:grid-cols-2 xl:grid-cols-3">
                {issuesData.data.map((issue) => (
                  <Card key={issue.id} className="border-l-4 border-l-primary">
                    <CardContent className="space-y-3 pt-4">
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm font-medium leading-snug">{issue.description}</p>
                        <Badge variant={issueStatusVariant(issue.status)}>{issue.status}</Badge>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <Badge variant={severityVariant(issue.severity)}>{issue.severity}</Badge>
                        {issue.is_overdue && (
                          <Badge variant="destructive">Overdue</Badge>
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        <p>Owner: {issue.owner_name ?? "—"}</p>
                        <p>Due: {issue.due_date}</p>
                        {issue.audit_title && <p>Audit: {issue.audit_title}</p>}
                      </div>
                      {canWriteAudits && issue.status !== "CLOSED" && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="w-full"
                          onClick={() => void handleCloseIssue(issue)}
                        >
                          Close Issue
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
              <PaginationBar
                page={issuesData.pagination.page}
                pages={issuesData.pagination.pages}
                total={issuesData.pagination.total}
                onPageChange={setPage}
              />
            </>
          )}
        </CardContent>
      </Card>

      <Dialog open={policyDialogOpen} onOpenChange={setPolicyDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Policy</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Title</Label>
              <Input
                value={policyForm.title}
                onChange={(e) => setPolicyForm({ ...policyForm, title: e.target.value })}
              />
            </div>
            <div>
              <Label>Version</Label>
              <Input
                value={policyForm.version}
                onChange={(e) => setPolicyForm({ ...policyForm, version: e.target.value })}
              />
            </div>
            <div>
              <Label>Effective Date</Label>
              <Input
                type="date"
                value={policyForm.effective_date}
                onChange={(e) => setPolicyForm({ ...policyForm, effective_date: e.target.value })}
              />
            </div>
            <div>
              <Label>Description</Label>
              <Textarea
                value={policyForm.description}
                onChange={(e) => setPolicyForm({ ...policyForm, description: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPolicyDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handleCreatePolicy()}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={auditDialogOpen} onOpenChange={setAuditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Schedule Audit</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Title</Label>
              <Input
                value={auditForm.title}
                onChange={(e) => setAuditForm({ ...auditForm, title: e.target.value })}
              />
            </div>
            <div>
              <Label>Department</Label>
              <Select
                value={auditForm.department_id}
                onChange={(e) => setAuditForm({ ...auditForm, department_id: e.target.value })}
              >
                <option value="">Select department</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name}
                  </option>
                ))}
              </Select>
            </div>
            <div>
              <Label>Auditor</Label>
              <Select
                value={auditForm.auditor_id}
                onChange={(e) => setAuditForm({ ...auditForm, auditor_id: e.target.value })}
              >
                <option value="">Select auditor</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name}
                  </option>
                ))}
              </Select>
            </div>
            <div>
              <Label>Audit Date</Label>
              <Input
                type="date"
                value={auditForm.audit_date}
                onChange={(e) => setAuditForm({ ...auditForm, audit_date: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAuditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handleCreateAudit()}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={issueDialogOpen} onOpenChange={setIssueDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Raise Compliance Issue</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Description</Label>
              <Textarea
                value={issueForm.description}
                onChange={(e) => setIssueForm({ ...issueForm, description: e.target.value })}
              />
            </div>
            <div>
              <Label>Owner</Label>
              <Select
                value={issueForm.owner_id}
                onChange={(e) => setIssueForm({ ...issueForm, owner_id: e.target.value })}
              >
                <option value="">Select owner</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name}
                  </option>
                ))}
              </Select>
            </div>
            <div>
              <Label>Severity</Label>
              <Select
                value={issueForm.severity}
                onChange={(e) =>
                  setIssueForm({
                    ...issueForm,
                    severity: e.target.value as ComplianceIssueInput["severity"],
                  })
                }
              >
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </Select>
            </div>
            <div>
              <Label>Due Date</Label>
              <Input
                type="date"
                value={issueForm.due_date}
                onChange={(e) => setIssueForm({ ...issueForm, due_date: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIssueDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handleCreateIssue()}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
