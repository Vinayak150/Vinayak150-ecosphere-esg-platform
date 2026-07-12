import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";

import type { PillarScore } from "../types/dashboard.types";

interface EsgScoreGaugeProps {
  overallScore: string;
  environmental: PillarScore;
  social: PillarScore;
  governance: PillarScore;
}

const PILLAR_COLORS = {
  environmental: "#16a34a",
  social: "#2563eb",
  governance: "#7c3aed",
};

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
    { label: "Environmental", score: environmental, color: PILLAR_COLORS.environmental },
    {
      label: "Social",
      score: social,
      color: social.available ? PILLAR_COLORS.social : PILLAR_COLORS.governance,
    },
    {
      label: "Governance",
      score: governance,
      color: governance.available ? PILLAR_COLORS.governance : PILLAR_COLORS.governance,
    },
  ];

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-base">Overall ESG Score</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative mx-auto h-48 w-48">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={gaugeData}
                dataKey="value"
                cx="50%"
                cy="50%"
                innerRadius={58}
                outerRadius={72}
                startAngle={220}
                endAngle={-40}
                stroke="none"
              >
                <Cell fill="#16a34a" />
                <Cell fill="hsl(var(--muted))" />
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold">{score.toFixed(1)}</span>
            <span className="text-xs text-muted-foreground">out of 100</span>
          </div>
        </div>
        <div className="mt-4 space-y-2">
          {pillars.map((pillar) => (
            <div key={pillar.label} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: pillar.color }}
                />
                <span>{pillar.label}</span>
              </div>
              <span className="font-medium">
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
