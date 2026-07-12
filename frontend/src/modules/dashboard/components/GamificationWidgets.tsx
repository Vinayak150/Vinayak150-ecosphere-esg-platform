import { Award, Target, Trophy } from "lucide-react";

import type { DashboardData } from "@/modules/dashboard/types/dashboard.types";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { EmptyState } from "@/shared/components/feedback/states";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";

interface GamificationWidgetsProps {
  data: DashboardData;
}

export function GamificationWidgets({ data }: GamificationWidgetsProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Trophy className="h-5 w-5 text-primary" />
        <h2 className="text-lg font-semibold">Gamification</h2>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Trophy className="h-4 w-4" />
              Top Performers
            </CardTitle>
          </CardHeader>
          <CardContent>
            {data.topPerformers.length === 0 ? (
              <EmptyState title="No performers yet" description="XP leaderboard data will appear here." />
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Rank</TableHead>
                    <TableHead>Employee</TableHead>
                    <TableHead>XP</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.topPerformers.map((entry) => (
                    <TableRow key={entry.employee_id}>
                      <TableCell>#{entry.rank}</TableCell>
                      <TableCell>{entry.employee_name}</TableCell>
                      <TableCell>{entry.total_xp}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Trophy className="h-4 w-4" />
              XP Leaderboard
            </CardTitle>
          </CardHeader>
          <CardContent>
            {data.xpLeaderboard.length === 0 ? (
              <EmptyState title="No XP data" description="Employee XP rankings will appear here." />
            ) : (
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
                  {data.xpLeaderboard.map((entry) => (
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
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Award className="h-4 w-4" />
              Recent Badge Unlocks
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.recentBadgeUnlocks.length === 0 ? (
              <EmptyState title="No recent unlocks" description="Badge awards will appear here." />
            ) : (
              data.recentBadgeUnlocks.map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded-md border p-3">
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{item.badge_icon ?? "🏅"}</span>
                    <div>
                      <p className="text-sm font-medium">{item.badge_name}</p>
                      <p className="text-xs text-muted-foreground">{item.employee_name}</p>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {new Date(item.earned_at).toLocaleDateString()}
                  </p>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Target className="h-4 w-4" />
              Challenge Progress
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {data.challengeProgress.length === 0 ? (
              <EmptyState title="No active challenges" description="Challenge progress will appear here." />
            ) : (
              data.challengeProgress.map((challenge) => (
                <div key={challenge.id} className="space-y-2 rounded-md border p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium">{challenge.title}</p>
                    <Badge variant="secondary">{challenge.status}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
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
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
