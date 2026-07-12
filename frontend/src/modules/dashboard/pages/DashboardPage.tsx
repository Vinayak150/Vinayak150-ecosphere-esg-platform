import { motion } from "framer-motion";
import { LayoutDashboard } from "lucide-react";

import { GamificationWidgets } from "@/modules/dashboard/components/GamificationWidgets";
import { DashboardCharts } from "@/modules/dashboard/components/DashboardCharts";
import { DepartmentRankingTable } from "@/modules/dashboard/components/DepartmentRankingTable";
import {
  EnvironmentalScoreCard,
  ExecutiveKpiCards,
} from "@/modules/dashboard/components/ExecutiveKpiCards";
import { EsgScoreGauge } from "@/modules/dashboard/components/EsgScoreGauge";
import { NotificationPanel } from "@/modules/dashboard/components/NotificationPanel";
import { QuickActions } from "@/modules/dashboard/components/QuickActions";
import { RecentActivityTimeline } from "@/modules/dashboard/components/RecentActivityTimeline";
import { RecentCarbonTransactionsTable } from "@/modules/dashboard/components/RecentCarbonTransactionsTable";
import { useDashboard } from "@/modules/dashboard/hooks/useDashboard";
import { ErrorState, LoadingSkeleton } from "@/shared/components/feedback/states";

export function DashboardPage() {
  const { data, isLoading, isError, refetch } = useDashboard();

  if (isLoading) {
    return (
      <div className="space-y-6 p-4 md:p-6">
        <LoadingSkeleton className="h-10 w-72" />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <LoadingSkeleton key={index} className="h-28 w-full" />
          ))}
        </div>
        <LoadingSkeleton className="h-80 w-full" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-4 md:p-6">
        <ErrorState
          title="Unable to load dashboard"
          message="The executive dashboard could not be loaded from the server."
          onRetry={() => void refetch()}
        />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="space-y-8 p-4 md:p-6"
    >
      <div>
        <div className="flex items-center gap-2">
          <LayoutDashboard className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold tracking-tight">Executive Dashboard</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          Real-time ESG performance aggregated from live platform data
        </p>
      </div>

      <ExecutiveKpiCards data={data} />

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="xl:col-span-1">
          <EsgScoreGauge
            overallScore={data.overallESG}
            environmental={data.environmentalScore}
            social={data.socialScore}
            governance={data.governanceScore}
          />
        </div>
        <div className="xl:col-span-2">
          <EnvironmentalScoreCard data={data} />
        </div>
      </div>

      <DashboardCharts data={data} />

      <GamificationWidgets data={data} />

      <div className="grid gap-6 lg:grid-cols-2">
        <DepartmentRankingTable rankings={data.departmentRanking} />
        <RecentCarbonTransactionsTable transactions={data.recentCarbonTransactions} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <RecentActivityTimeline activities={data.recentActivity} />
        <NotificationPanel notifications={data.notifications} />
      </div>

      <QuickActions actions={data.quickActions} />
    </motion.div>
  );
}
