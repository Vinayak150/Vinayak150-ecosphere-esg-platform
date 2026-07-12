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

import type { RecentCarbonTransaction } from "../types/dashboard.types";

interface RecentCarbonTransactionsTableProps {
  transactions: RecentCarbonTransaction[];
}

export function RecentCarbonTransactionsTable({
  transactions,
}: RecentCarbonTransactionsTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Recent Carbon Transactions</CardTitle>
      </CardHeader>
      <CardContent>
        {transactions.length === 0 ? (
          <EmptyState
            title="No transactions"
            description="Recent carbon transactions will be listed here."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Activity</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>CO₂</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map((tx) => (
                <TableRow key={tx.id}>
                  <TableCell className="font-medium">{tx.activity_name}</TableCell>
                  <TableCell>{tx.department_name ?? "—"}</TableCell>
                  <TableCell>{tx.emission_factor_name ?? "—"}</TableCell>
                  <TableCell>{Number(tx.calculated_emission).toFixed(2)} kg</TableCell>
                  <TableCell>{tx.transaction_date}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
