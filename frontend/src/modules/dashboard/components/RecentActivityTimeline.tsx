import { formatDistanceToNow } from "@/modules/dashboard/utils/format";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { EmptyState } from "@/shared/components/feedback/states";

import type { RecentActivity } from "../types/dashboard.types";

interface RecentActivityTimelineProps {
  activities: RecentActivity[];
}

export function RecentActivityTimeline({ activities }: RecentActivityTimelineProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-base">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        {activities.length === 0 ? (
          <EmptyState
            title="No recent activity"
            description="Platform actions will appear in this timeline."
          />
        ) : (
          <ol className="relative space-y-4 border-l border-muted pl-4">
            {activities.map((activity) => (
              <li key={activity.id} className="relative">
                <span className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-primary" />
                <p className="text-sm font-medium">{activity.message}</p>
                <p className="text-xs text-muted-foreground">
                  {activity.action} · {formatDistanceToNow(activity.created_at)}
                </p>
              </li>
            ))}
          </ol>
        )}
      </CardContent>
    </Card>
  );
}
