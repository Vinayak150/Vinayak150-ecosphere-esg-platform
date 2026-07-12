import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { EmptyState } from "@/shared/components/feedback/states";

import type { GovernanceAnalytics } from "../types/governance.types";

const SEVERITY_COLORS = ["#22c55e", "#eab308", "#f97316", "#ef4444"];

interface GovernanceChartsProps {
  analytics: GovernanceAnalytics;
}

export function GovernanceCharts({ analytics }: GovernanceChartsProps) {
  const scoreBreakdown = [
    { name: "Policy Completion", value: Number(analytics.policy_completion) },
    { name: "Compliance Rate", value: Number(analytics.compliance_rate) },
    {
      name: "Audit Completion",
      value:
        analytics.total_audits > 0
          ? (analytics.completed_audits / analytics.total_audits) * 100
          : 100,
    },
  ];

  const issueBreakdown = [
    { name: "Open", value: analytics.open_issues - analytics.overdue_issues },
    { name: "Overdue", value: analytics.overdue_issues },
    { name: "Closed", value: analytics.closed_issues },
  ].filter((item) => item.value > 0);

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Governance Score Breakdown</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={scoreBreakdown}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" name="Score %" fill="#7c3aed" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Compliance Issue Status</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          {issueBreakdown.length === 0 ? (
            <EmptyState
              title="No compliance issues"
              description="Issue status distribution will appear here."
            />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={issueBreakdown} dataKey="value" nameKey="name" outerRadius={90} label>
                  {issueBreakdown.map((_, index) => (
                    <Cell key={index} fill={SEVERITY_COLORS[index % SEVERITY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
