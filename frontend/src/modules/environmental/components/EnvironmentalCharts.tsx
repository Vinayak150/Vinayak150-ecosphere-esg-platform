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

import type { EnvironmentalAnalytics } from "../types/environmental.types";

interface ChartsProps {
  analytics: EnvironmentalAnalytics;
}

export function EnvironmentalCharts({ analytics }: ChartsProps) {
  const departmentData = analytics.department_carbon_totals.map((item) => ({
    name: item.department_name,
    emission: Number(item.total_emission),
  }));

  const trendData = analytics.monthly_carbon_trend.map((item) => ({
    month: item.month,
    emission: Number(item.total_emission),
  }));

  const sourcesData = analytics.top_carbon_sources.map((item) => ({
    name: item.emission_factor_name,
    value: Number(item.total_emission),
  }));

  const goalData = analytics.goal_progress.map((goal) => ({
    name: goal.title,
    progress: Number(goal.progress_percentage),
  }));

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Monthly Carbon Trend</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          {trendData.length === 0 ? (
            <EmptyState
              title="No trend data"
              description="Carbon transactions will populate this chart once recorded."
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
                  dataKey="emission"
                  name="CO₂ (kg)"
                  stroke={CHART_COLORS.primary}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Department Carbon Total</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          {departmentData.length === 0 ? (
            <EmptyState
              title="No department data"
              description="Department emissions will appear after carbon is logged."
            />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={departmentData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" tick={CHART_AXIS_STYLE} />
                <YAxis tick={CHART_AXIS_STYLE} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Legend />
                <Bar
                  dataKey="emission"
                  name="CO₂ (kg)"
                  fill={CHART_COLORS.primary}
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="text-base">Goal Progress</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          {goalData.length === 0 ? (
            <EmptyState
              title="No goals yet"
              description="Environmental goals will show progress here."
            />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={goalData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis type="number" domain={[0, 100]} tick={CHART_AXIS_STYLE} />
                <YAxis type="category" dataKey="name" width={140} tick={CHART_AXIS_STYLE} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Bar
                  dataKey="progress"
                  name="Progress %"
                  fill={CHART_COLORS.environmental[1]}
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="text-base">Top Carbon Sources</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          {sourcesData.length === 0 ? (
            <EmptyState
              title="No source data"
              description="Emission sources appear after carbon transactions are logged."
            />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sourcesData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ name, percent }) =>
                    `${name ?? ""} (${((percent ?? 0) * 100).toFixed(0)}%)`
                  }
                >
                  {sourcesData.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={CHART_COLORS.environmental[index % CHART_COLORS.environmental.length]}
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
    </div>
  );
}
