import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { EmptyState } from "@/shared/components/feedback/states";
import {
  CHART_AXIS_STYLE,
  CHART_COLORS,
  CHART_TOOLTIP_STYLE,
} from "@/shared/constants/chart-colors";

import type { SocialAnalytics } from "../types/social.types";

interface SocialChartsProps {
  analytics: SocialAnalytics;
}

export function SocialCharts({ analytics }: SocialChartsProps) {
  const trendData = analytics.monthly_csr_trend.map((point) => ({
    month: point.month,
    participations: point.participation_count,
    approved: point.approved_count,
  }));

  const departmentData = analytics.top_participating_departments.map((dept) => ({
    name: dept.department_name,
    value: dept.approved_participations,
  }));

  const departmentParticipation = analytics.department_participation.map((dept) => ({
    name: dept.department_name,
    rate: Number(dept.participation_rate),
  }));

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Monthly CSR Trend</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          {trendData.length === 0 ? (
            <EmptyState
              title="No CSR trend data"
              description="Participation records will populate this chart."
            />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="month" tick={CHART_AXIS_STYLE} />
                <YAxis tick={CHART_AXIS_STYLE} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="participations"
                  stroke={CHART_COLORS.socialPillar}
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="approved"
                  stroke={CHART_COLORS.social[2]}
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Top Participating Departments</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          {departmentData.length === 0 ? (
            <EmptyState
              title="No department data"
              description="Approved participations will appear here."
            />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={departmentData} dataKey="value" nameKey="name" outerRadius={90} label>
                  {departmentData.map((_, index) => (
                    <Cell
                      key={index}
                      fill={CHART_COLORS.social[index % CHART_COLORS.social.length]}
                    />
                  ))}
                </Pie>
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="text-base">Department Participation Rate</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          {departmentParticipation.length === 0 ? (
            <EmptyState
              title="No participation rates"
              description="Department participation metrics will display here."
            />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={departmentParticipation}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" tick={CHART_AXIS_STYLE} />
                <YAxis domain={[0, 100]} tick={CHART_AXIS_STYLE} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Bar
                  dataKey="rate"
                  name="Participation %"
                  fill={CHART_COLORS.socialPillar}
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
