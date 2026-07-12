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
          <ol className="relative space-y-5 border-l-2 border-primary/20 pl-5">
            {activities.map((activity) => (
              <li
                key={activity.id}
                className="relative rounded-lg border border-transparent p-2 transition-colors hover:border-muted hover:bg-muted/30"
              >
                <span className="absolute -left-[1.625rem] top-3 h-3 w-3 rounded-full border-2 border-background bg-primary shadow-sm ring-2 ring-primary/20" />
                <p className="text-sm font-medium leading-snug">{activity.message}</p>
                <p className="mt-1 text-xs text-muted-foreground">
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
