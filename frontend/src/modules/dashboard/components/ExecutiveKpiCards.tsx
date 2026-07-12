import { motion } from "framer-motion";
import { Activity, CheckCircle2, Leaf, Target, TrendingUp } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";

import type { DashboardData } from "../types/dashboard.types";

interface ExecutiveKpiCardsProps {
  data: DashboardData;
}

function formatScore(value: string): string {
  return Number(value).toFixed(1);
}

export function ExecutiveKpiCards({ data }: ExecutiveKpiCardsProps) {
  const totalEmissions = data.quickStats.find((stat) => stat.key === "total_emissions");
  const activeGoals = data.quickStats.find((stat) => stat.key === "active_goals");
  const completedGoals = data.quickStats.find((stat) => stat.key === "completed_goals");

  const cards = [
    {
      title: "Overall ESG Score",
      value: `${formatScore(data.overallESG)}%`,
      icon: TrendingUp,
      description: "Environmental (40%) + Social (30%) + Governance (30%)",
    },
    {
      title: "Environmental Score",
      value: data.environmentalScore.available
        ? `${formatScore(data.environmentalScore.score ?? "0")}%`
        : "N/A",
      icon: Leaf,
      description: "Goals and product ESG performance",
    },
    {
      title: "Total Emissions",
      value: totalEmissions?.value ?? "0 kg CO₂",
      icon: Activity,
      description: "Active carbon transactions",
    },
    {
      title: "Goal Completion",
      value: `${completedGoals?.value ?? "0"} / ${Number(completedGoals?.value ?? 0) + Number(activeGoals?.value ?? 0)}`,
      icon: Target,
      description: "Completed vs active goals",
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card, index) => (
        <motion.div
          key={card.title}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          <Card className="overflow-hidden">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.title}
              </CardTitle>
              <card.icon className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold tracking-tight">{card.value}</p>
              <p className="mt-1 text-xs text-muted-foreground">{card.description}</p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}

export function EnvironmentalScoreCard({ data }: ExecutiveKpiCardsProps) {
  const score = data.environmentalScore.available ? Number(data.environmentalScore.score ?? 0) : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Leaf className="h-4 w-4 text-primary" />
          Environmental Performance
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-end justify-between">
          <div>
            <p className="text-3xl font-bold">{score.toFixed(1)}%</p>
            <p className="text-sm text-muted-foreground">Live environmental pillar score</p>
          </div>
          <CheckCircle2 className="h-8 w-8 text-primary" />
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-muted">
          <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${Math.min(score, 100)}%` }} />
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-md border p-3">
            <p className="text-muted-foreground">Goals tracked</p>
            <p className="font-semibold">{data.goalProgress.length}</p>
          </div>
          <div className="rounded-md border p-3">
            <p className="text-muted-foreground">Carbon sources</p>
            <p className="font-semibold">{data.topCarbonSources.length}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
