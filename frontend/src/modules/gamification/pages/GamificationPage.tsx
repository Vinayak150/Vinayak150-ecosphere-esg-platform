import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  Award,
  Check,
  Gift,
  Medal,
  Plus,
  Search,
  Target,
  Trash2,
  Trophy,
  X,
} from "lucide-react";

import { usePermission } from "@/modules/auth/hooks/usePermission";
import { GamificationCharts } from "@/modules/gamification/components/GamificationCharts";
import {
  useBadges,
  useBadgeMutations,
  useChallengeMutations,
  useChallenges,
  useCompanyLeaderboard,
  useDepartmentLeaderboard,
  useEmployeeBadges,
  useGamificationAnalytics,
  useParticipationMutations,
  useParticipations,
  useRewardMutations,
  useRewards,
} from "@/modules/gamification/hooks/useGamification";
import type {
  Badge,
  BadgeInput,
  Challenge,
  ChallengeInput,
  Participation,
  Reward,
  RewardInput,
} from "@/modules/gamification/types/gamification.types";
import { Badge as UiBadge } from "@/shared/components/ui/badge";
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

function approvalVariant(status: string): "default" | "secondary" | "destructive" {
  if (status === "APPROVED") return "default";
  if (status === "REJECTED") return "destructive";
  return "secondary";
}

function challengeStatusVariant(status: string): "default" | "secondary" | "destructive" {
  if (status === "ACTIVE") return "default";
  if (status === "COMPLETED") return "secondary";
  if (status === "ARCHIVED") return "destructive";
  return "secondary";
}

export function GamificationPage() {
  const canWrite = usePermission("challenges:write");
  const canParticipate = usePermission("challenges:participate");
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

  const { data: analytics, isLoading: analyticsLoading, isError, refetch } = useGamificationAnalytics();
  const { data: challengesData, isLoading: challengesLoading } = useChallenges(listParams);
  const { data: participationsData, isLoading: participationsLoading } = useParticipations(listParams);
  const { data: badgesData } = useBadges({ page: 1, page_size: 50 });
  const { data: employeeBadgesData } = useEmployeeBadges({ page: 1, page_size: 12 });
  const { data: rewardsData } = useRewards({ page: 1, page_size: 50, status: "ACTIVE" });
  const { data: companyLeaderboard = [] } = useCompanyLeaderboard();
  const { data: departmentLeaderboard = [] } = useDepartmentLeaderboard();

  const challengeMutations = useChallengeMutations();
  const participationMutations = useParticipationMutations();
  const badgeMutations = useBadgeMutations();
  const rewardMutations = useRewardMutations();

  const [challengeDialogOpen, setChallengeDialogOpen] = useState(false);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [badgeDialogOpen, setBadgeDialogOpen] = useState(false);
  const [rewardDialogOpen, setRewardDialogOpen] = useState(false);
  const [editingChallenge, setEditingChallenge] = useState<Challenge | null>(null);
  const [selectedChallenge, setSelectedChallenge] = useState<Challenge | null>(null);

  const defaultDeadline = new Date();
  defaultDeadline.setDate(defaultDeadline.getDate() + 30);

  const [challengeForm, setChallengeForm] = useState<ChallengeInput>({
    title: "",
    category: "",
    description: "",
    xp: 50,
    difficulty: "MEDIUM",
    evidence_required: false,
    deadline: defaultDeadline.toISOString().slice(0, 10),
    status: "DRAFT",
  });

  const [badgeForm, setBadgeForm] = useState<BadgeInput>({
    name: "",
    description: "",
    unlock_rule: { rule: "total_xp", threshold: 100 },
    icon: "🏅",
    status: "ACTIVE",
  });

  const [rewardForm, setRewardForm] = useState<RewardInput>({
    name: "",
    description: "",
    points_required: 100,
    stock: 10,
    status: "ACTIVE",
  });

  function resetChallengeForm() {
    setEditingChallenge(null);
    setChallengeForm({
      title: "",
      category: "",
      description: "",
      xp: 50,
      difficulty: "MEDIUM",
      evidence_required: false,
      deadline: defaultDeadline.toISOString().slice(0, 10),
      status: "DRAFT",
    });
  }

  async function handleChallengeSubmit() {
    try {
      if (editingChallenge) {
        await challengeMutations.update.mutateAsync({ id: editingChallenge.id, payload: challengeForm });
        toast({ title: "Challenge updated" });
      } else {
        await challengeMutations.create.mutateAsync(challengeForm);
        toast({ title: "Challenge created" });
      }
      setChallengeDialogOpen(false);
      resetChallengeForm();
    } catch {
      toast({ title: "Failed to save challenge", variant: "destructive" });
    }
  }

  async function handleJoinChallenge(challengeId: string) {
    try {
      await participationMutations.join.mutateAsync({ challenge_id: challengeId });
      toast({ title: "Joined challenge" });
    } catch {
      toast({ title: "Failed to join challenge", variant: "destructive" });
    }
  }

  async function handleSubmitParticipation(participation: Participation) {
    try {
      await participationMutations.submit.mutateAsync({
        id: participation.id,
        payload: {
          progress: 100,
          proof_file: participation.proof_file ?? "submission-proof.pdf",
        },
      });
      toast({ title: "Participation submitted for review" });
    } catch {
      toast({ title: "Submission failed", variant: "destructive" });
    }
  }

  async function handleBadgeSubmit() {
    try {
      await badgeMutations.create.mutateAsync(badgeForm);
      toast({ title: "Badge created" });
      setBadgeDialogOpen(false);
      setBadgeForm({
        name: "",
        description: "",
        unlock_rule: { rule: "total_xp", threshold: 100 },
        icon: "🏅",
        status: "ACTIVE",
      });
    } catch {
      toast({ title: "Failed to create badge", variant: "destructive" });
    }
  }

  async function handleRewardSubmit() {
    try {
      await rewardMutations.create.mutateAsync(rewardForm);
      toast({ title: "Reward created" });
      setRewardDialogOpen(false);
      setRewardForm({
        name: "",
        description: "",
        points_required: 100,
        stock: 10,
        status: "ACTIVE",
      });
    } catch {
      toast({ title: "Failed to create reward", variant: "destructive" });
    }
  }

  async function handleRedeemReward(rewardId: string) {
    try {
      await rewardMutations.redeem.mutateAsync({ reward_id: rewardId });
      toast({ title: "Reward redeemed successfully" });
    } catch {
      toast({ title: "Redemption failed", variant: "destructive" });
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
          title="Unable to load gamification data"
          message="The gamification dashboard could not be loaded."
          onRetry={() => void refetch()}
        />
      </div>
    );
  }

  const pendingReviews =
    participationsData?.data.filter((p) => p.approval_status === "SUBMITTED") ?? [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 p-4 md:p-6"
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Trophy className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold tracking-tight">Gamification Hub</h1>
          </div>
          <p className="text-sm text-muted-foreground">
            Challenges, badges, rewards, and leaderboards powered by live XP data
          </p>
        </div>
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            className="pl-9"
            placeholder="Search challenges..."
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
            <CardTitle className="text-sm font-medium text-muted-foreground">Total XP</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{analytics.total_xp}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Completion Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {Number(analytics.challenge_completion_rate).toFixed(1)}%
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Challenges</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{analytics.active_challenges}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Pending Reviews</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{analytics.pending_reviews}</p>
          </CardContent>
        </Card>
      </div>

      <GamificationCharts analytics={analytics} />

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {challengesData?.data
          .filter((c) => c.status === "ACTIVE" || c.status === "UNDER_REVIEW")
          .slice(0, 3)
          .map((challenge) => (
            <Card key={challenge.id}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base">{challenge.title}</CardTitle>
                  <UiBadge variant={challengeStatusVariant(challenge.status)}>{challenge.status}</UiBadge>
                </div>
                <p className="text-xs text-muted-foreground">{challenge.category}</p>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p className="text-muted-foreground">
                  {challenge.approved_count}/{challenge.participation_count} completed · {challenge.xp} XP
                </p>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-primary"
                    style={{
                      width: `${
                        challenge.participation_count > 0
                          ? (challenge.approved_count / challenge.participation_count) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => {
                    setSelectedChallenge(challenge);
                    setDetailDialogOpen(true);
                  }}
                >
                  View Details
                </Button>
              </CardContent>
            </Card>
          ))}
      </section>

      {canWrite ? (
        <section className="rounded-lg border bg-card shadow-sm">
          <div className="flex items-center justify-between border-b p-4">
            <h2 className="text-lg font-semibold">Review Queue</h2>
            <UiBadge>{pendingReviews.length} submitted</UiBadge>
          </div>
          {participationsLoading ? (
            <div className="p-4">
              <LoadingSkeleton className="h-24 w-full" />
            </div>
          ) : pendingReviews.length === 0 ? (
            <div className="p-4">
              <EmptyState title="No pending reviews" description="All submissions have been processed." />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Challenge</TableHead>
                  <TableHead>Proof</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pendingReviews.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.employee_name}</TableCell>
                    <TableCell>{item.challenge_title}</TableCell>
                    <TableCell className="max-w-[200px] truncate">{item.proof_file ?? "—"}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          size="sm"
                          onClick={async () => {
                            try {
                              await participationMutations.approve.mutateAsync(item.id);
                              toast({ title: "Participation approved, XP awarded" });
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

      <section className="rounded-lg border bg-card shadow-sm">
        <div className="flex flex-col gap-3 border-b p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Challenges</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            <Select
              value={approvalFilter}
              onChange={(e) => {
                setApprovalFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All participations</option>
              <option value="PENDING">Pending</option>
              <option value="SUBMITTED">Submitted</option>
              <option value="APPROVED">Approved</option>
              <option value="REJECTED">Rejected</option>
            </Select>
            {canWrite ? (
              <Button
                onClick={() => {
                  resetChallengeForm();
                  setChallengeDialogOpen(true);
                }}
              >
                <Plus className="mr-2 h-4 w-4" />
                New Challenge
              </Button>
            ) : null}
          </div>
        </div>
        {challengesLoading ? (
          <div className="p-4">
            <LoadingSkeleton className="h-32 w-full" />
          </div>
        ) : !challengesData?.data.length ? (
          <div className="p-4">
            <EmptyState title="No challenges" description="Create a challenge to get started." />
          </div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>XP</TableHead>
                  <TableHead>Difficulty</TableHead>
                  <TableHead>Deadline</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {challengesData.data.map((challenge) => (
                  <TableRow key={challenge.id}>
                    <TableCell className="font-medium">{challenge.title}</TableCell>
                    <TableCell>{challenge.category}</TableCell>
                    <TableCell>{challenge.xp}</TableCell>
                    <TableCell>{challenge.difficulty}</TableCell>
                    <TableCell>{challenge.deadline}</TableCell>
                    <TableCell>
                      <UiBadge variant={challengeStatusVariant(challenge.status)}>
                        {challenge.status}
                      </UiBadge>
                    </TableCell>
                    <TableCell>
                      {challenge.approved_count}/{challenge.participation_count}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        {canParticipate && challenge.status === "ACTIVE" ? (
                          <Button size="sm" variant="outline" onClick={() => void handleJoinChallenge(challenge.id)}>
                            Join
                          </Button>
                        ) : null}
                        {canWrite ? (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                setEditingChallenge(challenge);
                                setChallengeForm({
                                  title: challenge.title,
                                  category: challenge.category,
                                  description: challenge.description ?? "",
                                  xp: challenge.xp,
                                  difficulty: challenge.difficulty,
                                  evidence_required: challenge.evidence_required,
                                  deadline: challenge.deadline,
                                  status: challenge.status,
                                });
                                setChallengeDialogOpen(true);
                              }}
                            >
                              Edit
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={async () => {
                                try {
                                  await challengeMutations.remove.mutateAsync(challenge.id);
                                  toast({ title: "Challenge deleted" });
                                } catch {
                                  toast({ title: "Delete failed", variant: "destructive" });
                                }
                              }}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </>
                        ) : null}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <PaginationBar
              page={challengesData.pagination.page}
              pages={challengesData.pagination.pages}
              total={challengesData.pagination.total}
              onPageChange={setPage}
            />
          </>
        )}
      </section>

      <section className="rounded-lg border bg-card shadow-sm">
        <div className="flex items-center gap-2 border-b p-4">
          <Medal className="h-5 w-5 text-primary" />
          <h2 className="text-lg font-semibold">Participation</h2>
        </div>
        {participationsLoading ? (
          <div className="p-4">
            <LoadingSkeleton className="h-32 w-full" />
          </div>
        ) : !participationsData?.data.length ? (
          <div className="p-4">
            <EmptyState title="No participations" description="Join a challenge to appear here." />
          </div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Challenge</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>XP</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {participationsData.data.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.employee_name}</TableCell>
                    <TableCell>{item.challenge_title}</TableCell>
                    <TableCell>{item.progress}%</TableCell>
                    <TableCell>
                      <UiBadge variant={approvalVariant(item.approval_status)}>
                        {item.approval_status}
                      </UiBadge>
                    </TableCell>
                    <TableCell>{item.xp_awarded}</TableCell>
                    <TableCell className="text-right">
                      {canParticipate && item.approval_status === "PENDING" ? (
                        <Button size="sm" onClick={() => void handleSubmitParticipation(item)}>
                          Submit
                        </Button>
                      ) : null}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <PaginationBar
              page={participationsData.pagination.page}
              pages={participationsData.pagination.pages}
              total={participationsData.pagination.total}
              onPageChange={setPage}
            />
          </>
        )}
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg border bg-card shadow-sm">
          <div className="flex items-center justify-between border-b p-4">
            <div className="flex items-center gap-2">
              <Award className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">Badge Gallery</h2>
            </div>
            {canWrite ? (
              <Button size="sm" onClick={() => setBadgeDialogOpen(true)}>
                <Plus className="mr-1 h-4 w-4" />
                Add Badge
              </Button>
            ) : null}
          </div>
          <div className="grid gap-4 p-4 sm:grid-cols-2">
            {badgesData?.data.map((badge: Badge) => (
              <Card key={badge.id}>
                <CardContent className="flex items-start gap-3 p-4">
                  <span className="text-3xl">{badge.icon ?? "🏅"}</span>
                  <div>
                    <p className="font-semibold">{badge.name}</p>
                    <p className="text-xs text-muted-foreground">{badge.description}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {badge.earned_count} earned · {JSON.stringify(badge.unlock_rule)}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        <section className="rounded-lg border bg-card shadow-sm">
          <div className="flex items-center gap-2 border-b p-4">
            <Trophy className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Recent Badge Unlocks</h2>
          </div>
          <div className="space-y-3 p-4">
            {employeeBadgesData?.data.length ? (
              employeeBadgesData.data.map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded-md border p-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{item.badge_icon ?? "🏅"}</span>
                    <div>
                      <p className="font-medium">{item.badge_name}</p>
                      <p className="text-xs text-muted-foreground">{item.employee_name}</p>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {new Date(item.earned_at).toLocaleDateString()}
                  </p>
                </div>
              ))
            ) : (
              <EmptyState title="No badges earned yet" description="Badges unlock automatically when criteria are met." />
            )}
          </div>
        </section>
      </div>

      <section className="rounded-lg border bg-card shadow-sm">
        <div className="flex items-center justify-between border-b p-4">
          <div className="flex items-center gap-2">
            <Gift className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Reward Store</h2>
          </div>
          {canWrite ? (
            <Button size="sm" onClick={() => setRewardDialogOpen(true)}>
              <Plus className="mr-1 h-4 w-4" />
              Add Reward
            </Button>
          ) : null}
        </div>
        <div className="grid gap-4 p-4 sm:grid-cols-2 lg:grid-cols-3">
          {rewardsData?.data.map((reward: Reward) => (
            <Card key={reward.id}>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{reward.name}</CardTitle>
                <p className="text-xs text-muted-foreground">{reward.description}</p>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span>{reward.points_required} XP</span>
                  <UiBadge variant={reward.stock > 0 ? "default" : "destructive"}>
                    {reward.stock} in stock
                  </UiBadge>
                </div>
                {canParticipate ? (
                  <Button
                    className="w-full"
                    size="sm"
                    disabled={reward.stock <= 0 || reward.status !== "ACTIVE"}
                    onClick={() => void handleRedeemReward(reward.id)}
                  >
                    Redeem
                  </Button>
                ) : null}
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg border bg-card shadow-sm">
          <div className="flex items-center gap-2 border-b p-4">
            <Trophy className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Company Leaderboard</h2>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rank</TableHead>
                <TableHead>Employee</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>XP</TableHead>
                <TableHead>Badges</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {companyLeaderboard.map((entry) => (
                <TableRow key={entry.employee_id}>
                  <TableCell>#{entry.rank}</TableCell>
                  <TableCell>{entry.employee_name}</TableCell>
                  <TableCell>{entry.department_name ?? "—"}</TableCell>
                  <TableCell>{entry.total_xp}</TableCell>
                  <TableCell>{entry.badge_count}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </section>

        <section className="rounded-lg border bg-card shadow-sm">
          <div className="flex items-center gap-2 border-b p-4">
            <Trophy className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Department Leaderboard</h2>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rank</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Total XP</TableHead>
                <TableHead>Employees</TableHead>
                <TableHead>Avg XP</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {departmentLeaderboard.map((entry) => (
                <TableRow key={entry.department_id}>
                  <TableCell>#{entry.rank}</TableCell>
                  <TableCell>{entry.department_name}</TableCell>
                  <TableCell>{entry.total_xp}</TableCell>
                  <TableCell>{entry.employee_count}</TableCell>
                  <TableCell>{Number(entry.average_xp).toFixed(1)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </section>
      </div>

      <Dialog open={challengeDialogOpen} onOpenChange={setChallengeDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingChallenge ? "Edit Challenge" : "New Challenge"}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            <div className="grid gap-2">
              <Label>Title</Label>
              <Input
                value={challengeForm.title}
                onChange={(e) => setChallengeForm({ ...challengeForm, title: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label>Category</Label>
              <Input
                value={challengeForm.category}
                onChange={(e) => setChallengeForm({ ...challengeForm, category: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label>Description</Label>
              <Textarea
                value={challengeForm.description}
                onChange={(e) => setChallengeForm({ ...challengeForm, description: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label>XP</Label>
                <Input
                  type="number"
                  value={challengeForm.xp}
                  onChange={(e) =>
                    setChallengeForm({ ...challengeForm, xp: Number(e.target.value) })
                  }
                />
              </div>
              <div className="grid gap-2">
                <Label>Deadline</Label>
                <Input
                  type="date"
                  value={challengeForm.deadline}
                  onChange={(e) => setChallengeForm({ ...challengeForm, deadline: e.target.value })}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label>Difficulty</Label>
                <Select
                  value={challengeForm.difficulty}
                  onChange={(e) =>
                    setChallengeForm({
                      ...challengeForm,
                      difficulty: e.target.value as ChallengeInput["difficulty"],
                    })
                  }
                >
                  <option value="EASY">Easy</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HARD">Hard</option>
                  <option value="EXPERT">Expert</option>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label>Status</Label>
                <Select
                  value={challengeForm.status}
                  onChange={(e) =>
                    setChallengeForm({
                      ...challengeForm,
                      status: e.target.value as ChallengeInput["status"],
                    })
                  }
                >
                  <option value="DRAFT">Draft</option>
                  <option value="ACTIVE">Active</option>
                  <option value="UNDER_REVIEW">Under Review</option>
                  <option value="COMPLETED">Completed</option>
                  <option value="ARCHIVED">Archived</option>
                </Select>
              </div>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={challengeForm.evidence_required}
                onChange={(e) =>
                  setChallengeForm({ ...challengeForm, evidence_required: e.target.checked })
                }
              />
              Evidence required
            </label>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setChallengeDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handleChallengeSubmit()}>
              {editingChallenge ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{selectedChallenge?.title}</DialogTitle>
          </DialogHeader>
          {selectedChallenge ? (
            <div className="space-y-3 text-sm">
              <p>{selectedChallenge.description}</p>
              <div className="grid grid-cols-2 gap-2">
                <p>
                  <span className="text-muted-foreground">Category:</span> {selectedChallenge.category}
                </p>
                <p>
                  <span className="text-muted-foreground">XP:</span> {selectedChallenge.xp}
                </p>
                <p>
                  <span className="text-muted-foreground">Difficulty:</span> {selectedChallenge.difficulty}
                </p>
                <p>
                  <span className="text-muted-foreground">Deadline:</span> {selectedChallenge.deadline}
                </p>
                <p>
                  <span className="text-muted-foreground">Evidence:</span>{" "}
                  {selectedChallenge.evidence_required ? "Required" : "Optional"}
                </p>
                <p>
                  <span className="text-muted-foreground">Status:</span> {selectedChallenge.status}
                </p>
              </div>
              <p>
                Progress: {selectedChallenge.approved_count}/{selectedChallenge.participation_count}{" "}
                completed
              </p>
            </div>
          ) : null}
        </DialogContent>
      </Dialog>

      <Dialog open={badgeDialogOpen} onOpenChange={setBadgeDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Badge</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            <div className="grid gap-2">
              <Label>Name</Label>
              <Input
                value={badgeForm.name}
                onChange={(e) => setBadgeForm({ ...badgeForm, name: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label>Description</Label>
              <Textarea
                value={badgeForm.description}
                onChange={(e) => setBadgeForm({ ...badgeForm, description: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label>Icon</Label>
              <Input
                value={badgeForm.icon}
                onChange={(e) => setBadgeForm({ ...badgeForm, icon: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setBadgeDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handleBadgeSubmit()}>Create Badge</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={rewardDialogOpen} onOpenChange={setRewardDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Reward</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            <div className="grid gap-2">
              <Label>Name</Label>
              <Input
                value={rewardForm.name}
                onChange={(e) => setRewardForm({ ...rewardForm, name: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label>Description</Label>
              <Textarea
                value={rewardForm.description}
                onChange={(e) => setRewardForm({ ...rewardForm, description: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label>Points Required</Label>
                <Input
                  type="number"
                  value={rewardForm.points_required}
                  onChange={(e) =>
                    setRewardForm({ ...rewardForm, points_required: Number(e.target.value) })
                  }
                />
              </div>
              <div className="grid gap-2">
                <Label>Stock</Label>
                <Input
                  type="number"
                  value={rewardForm.stock}
                  onChange={(e) => setRewardForm({ ...rewardForm, stock: Number(e.target.value) })}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRewardDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void handleRewardSubmit()}>Create Reward</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}
