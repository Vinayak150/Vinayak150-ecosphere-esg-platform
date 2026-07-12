import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

import { AnimatedCounter } from "@/shared/components/ui/animated-counter";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { CHART_COLORS } from "@/shared/constants/chart-colors";

import type { PillarScore } from "../types/dashboard.types";

interface EsgScoreGaugeProps {
  overallScore: string;
  environmental: PillarScore;
  social: PillarScore;
  governance: PillarScore;
}

export function EsgScoreGauge({
  overallScore,
  environmental,
  social,
  governance,
}: EsgScoreGaugeProps) {
  const score = Number(overallScore);
  const gaugeData = [
    { name: "score", value: score },
    { name: "remaining", value: Math.max(0, 100 - score) },
  ];

  const pillars = [
    { label: "Environmental", score: environmental, color: CHART_COLORS.primary },
    { label: "Social", score: social, color: CHART_COLORS.socialPillar },
    { label: "Governance", score: governance, color: CHART_COLORS.governancePillar },
  ];

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-base font-semibold">Overall ESG Score</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative mx-auto h-52 w-52">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={gaugeData}
                dataKey="value"
                cx="50%"
                cy="50%"
                innerRadius={62}
                outerRadius={78}
                startAngle={220}
                endAngle={-40}
                stroke="none"
              >
                <Cell fill={CHART_COLORS.primary} />
                <Cell fill={CHART_COLORS.muted} />
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <AnimatedCounter
              value={score}
              decimals={1}
              className="text-4xl font-bold tracking-tight"
            />
            <span className="text-xs text-muted-foreground">out of 100</span>
          </div>
        </div>
        <div className="mt-5 space-y-3">
          {pillars.map((pillar) => (
            <div
              key={pillar.label}
              className="flex items-center justify-between rounded-lg border bg-muted/20 px-3 py-2 text-sm"
            >
              <div className="flex items-center gap-2">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: pillar.color }}
                  aria-hidden
                />
                <span>{pillar.label}</span>
              </div>
              <span className="font-semibold">
                {pillar.score.available
                  ? `${Number(pillar.score.score ?? 0).toFixed(1)}%`
                  : "Not available"}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
