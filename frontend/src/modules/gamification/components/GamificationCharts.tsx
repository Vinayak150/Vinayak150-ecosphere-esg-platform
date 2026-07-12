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

import type { GamificationAnalytics } from "../types/gamification.types";

const CHART_COLORS = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#1d4ed8", "#7c3aed"];

interface GamificationChartsProps {
  analytics: GamificationAnalytics;
}

export function GamificationCharts({ analytics }: GamificationChartsProps) {
  const badgeData = analytics.badge_distribution.map((item) => ({
    name: item.badge_name,
    value: item.earned_count,
  }));

  const departmentData = analytics.top_departments.map((item) => ({
    name: item.department_name,
    xp: item.total_xp,
    employees: item.employee_count,
  }));

  const topEmployees = analytics.top_employees.map((item) => ({
    name: item.employee_name,
    xp: item.total_xp,
    badges: item.badge_count,
  }));

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Badge Distribution</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          {badgeData.length === 0 ? (
            <EmptyState
              title="No badge awards yet"
              description="Badge distribution will appear as employees earn badges."
            />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={badgeData} dataKey="value" nameKey="name" outerRadius={90} label>
                  {badgeData.map((_, index) => (
                    <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Top Departments by XP</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          {departmentData.length === 0 ? (
            <EmptyState
              title="No department XP data"
              description="Department rankings will appear after challenge completions."
            />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={departmentData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="xp" name="Total XP" fill="#7c3aed" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="text-base">Top Employees</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          {topEmployees.length === 0 ? (
            <EmptyState
              title="No leaderboard data"
              description="Employee rankings will appear after XP is awarded."
            />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topEmployees}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="xp" name="Total XP" fill="#2563eb" radius={[4, 4, 0, 0]} />
                <Bar dataKey="badges" name="Badges" fill="#22c55e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
