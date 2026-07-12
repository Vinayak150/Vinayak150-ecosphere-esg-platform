import { Medal } from "lucide-react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { EmptyState } from "@/shared/components/feedback/states";
import { cn } from "@/shared/lib/utils";

import type { DepartmentRankingItem } from "../types/dashboard.types";

interface DepartmentRankingTableProps {
  rankings: DepartmentRankingItem[];
}

function rankDisplay(rank: number) {
  if (rank === 1) return { label: "#1", className: "text-amber-600" };
  if (rank === 2) return { label: "#2", className: "text-slate-500" };
  if (rank === 3) return { label: "#3", className: "text-amber-700" };
  return { label: `#${rank}`, className: "text-muted-foreground" };
}

export function DepartmentRankingTable({ rankings }: DepartmentRankingTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Medal className="h-4 w-4 text-primary" />
          Department Ranking
        </CardTitle>
      </CardHeader>
      <CardContent>
        {rankings.length === 0 ? (
          <EmptyState
            title="No department rankings"
            description="Rankings appear when departments have carbon and goal data."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rank</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Emissions</TableHead>
                <TableHead>Goals</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rankings.map((row) => {
                const rank = rankDisplay(row.rank);
                return (
                  <TableRow key={row.department_id}>
                    <TableCell className={cn("font-semibold tabular-nums", rank.className)}>
                      {rank.label}
                    </TableCell>
                    <TableCell className="font-medium">{row.department_name}</TableCell>
                    <TableCell className="tabular-nums">
                      {Number(row.environmental_score).toFixed(1)}%
                    </TableCell>
                    <TableCell className="tabular-nums">
                      {Number(row.total_emission).toLocaleString()} kg
                    </TableCell>
                    <TableCell className="tabular-nums">
                      {row.goals_completed}/{row.goals_total}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
