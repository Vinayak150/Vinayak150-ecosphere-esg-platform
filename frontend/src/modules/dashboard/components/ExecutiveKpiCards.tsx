import { Activity, Leaf, Target, TrendingUp } from "lucide-react";

import { AnimatedCounter } from "@/shared/components/ui/animated-counter";
import { KpiCard } from "@/shared/components/layout/KpiCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";

import type { DashboardData } from "../types/dashboard.types";

interface ExecutiveKpiCardsProps {
  data: DashboardData;
}

function formatScore(value: string): number {
  return Number(value);
}

export function ExecutiveKpiCards({ data }: ExecutiveKpiCardsProps) {
  const totalEmissions = data.quickStats.find((stat) => stat.key === "total_emissions");
  const activeGoals = data.quickStats.find((stat) => stat.key === "active_goals");
  const completedGoals = data.quickStats.find((stat) => stat.key === "completed_goals");

  const envScore = data.environmentalScore.available
    ? formatScore(data.environmentalScore.score ?? "0")
    : null;

  const cards = [
    {
      title: "Overall ESG Score",
      value: <AnimatedCounter value={formatScore(data.overallESG)} suffix="%" className="text-2xl font-bold tracking-tight" />,
      icon: TrendingUp,
      description: "Environmental (40%) + Social (30%) + Governance (30%)",
    },
    {
      title: "Environmental Score",
      value: envScore !== null ? (
        <AnimatedCounter value={envScore} suffix="%" className="text-2xl font-bold tracking-tight" />
      ) : (
        <span className="text-2xl font-bold tracking-tight">N/A</span>
      ),
      icon: Leaf,
      description: "Goals and product ESG performance",
    },
    {
      title: "Total Emissions",
      value: <span className="text-2xl font-bold tracking-tight">{totalEmissions?.value ?? "0 kg CO₂"}</span>,
      icon: Activity,
      description: "Active carbon transactions",
    },
    {
      title: "Goal Completion",
      value: (
        <span className="text-2xl font-bold tracking-tight">
          {completedGoals?.value ?? "0"} /{" "}
          {Number(completedGoals?.value ?? 0) + Number(activeGoals?.value ?? 0)}
        </span>
      ),
      icon: Target,
      description: "Completed vs active goals",
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card, index) => (
        <KpiCard
          key={card.title}
          title={card.title}
          value={card.value}
          description={card.description}
          icon={card.icon}
          index={index}
        />
      ))}
    </div>
  );
}

export function EnvironmentalScoreCard({ data }: ExecutiveKpiCardsProps) {
  const score = data.environmentalScore.available ? Number(data.environmentalScore.score ?? 0) : 0;

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10">
            <Leaf className="h-4 w-4 text-primary" aria-hidden />
          </div>
          Environmental Performance
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="flex items-end justify-between">
          <div>
            <p className="text-3xl font-bold tracking-tight">
              <AnimatedCounter value={score} suffix="%" decimals={1} />
            </p>
            <p className="text-sm text-muted-foreground">Live environmental pillar score</p>
          </div>
        </div>
        <div className="h-2.5 overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary transition-all duration-500 ease-out"
            style={{ width: `${Math.min(score, 100)}%` }}
          />
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-lg border bg-muted/20 p-3 transition-colors hover:bg-muted/40">
            <p className="text-muted-foreground">Goals tracked</p>
            <p className="text-lg font-semibold">{data.goalProgress.length}</p>
          </div>
          <div className="rounded-lg border bg-muted/20 p-3 transition-colors hover:bg-muted/40">
            <p className="text-muted-foreground">Carbon sources</p>
            <p className="text-lg font-semibold">{data.topCarbonSources.length}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
