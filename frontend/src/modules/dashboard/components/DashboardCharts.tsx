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

import type { DashboardData } from "../types/dashboard.types";

interface DashboardChartsProps {
  data: DashboardData;
}

export function DashboardCharts({ data }: DashboardChartsProps) {
  const trendData = data.monthlyCarbonTrend.map((point) => ({
    month: point.month,
    emission: Number(point.total_emission),
  }));

  const sourcesData = data.topCarbonSources.map((source) => ({
    name: source.emission_factor_name,
    value: Number(source.total_emission),
  }));

  const goalData = data.goalProgress.map((goal) => ({
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
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card>
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
                <Pie data={sourcesData} dataKey="value" nameKey="name" outerRadius={90} label>
                  {sourcesData.map((_, index) => (
                    <Cell
                      key={index}
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
    </div>
  );
}
