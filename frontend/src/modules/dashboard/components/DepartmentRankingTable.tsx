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

import type { DepartmentRankingItem } from "../types/dashboard.types";

interface DepartmentRankingTableProps {
  rankings: DepartmentRankingItem[];
}

export function DepartmentRankingTable({ rankings }: DepartmentRankingTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Department Ranking</CardTitle>
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
              {rankings.map((row) => (
                <TableRow key={row.department_id}>
                  <TableCell className="font-medium">#{row.rank}</TableCell>
                  <TableCell>{row.department_name}</TableCell>
                  <TableCell>{Number(row.environmental_score).toFixed(1)}%</TableCell>
                  <TableCell>{Number(row.total_emission).toLocaleString()} kg</TableCell>
                  <TableCell>
                    {row.goals_completed}/{row.goals_total}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
