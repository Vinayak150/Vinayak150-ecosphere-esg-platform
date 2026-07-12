import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { EmptyState } from "@/shared/components/feedback/states";

import type { DashboardNotification } from "../types/dashboard.types";

interface NotificationPanelProps {
  notifications: DashboardNotification[];
}

function severityVariant(severity: string): "default" | "secondary" | "destructive" {
  if (severity === "high") return "destructive";
  if (severity === "medium") return "default";
  return "secondary";
}

export function NotificationPanel({ notifications }: NotificationPanelProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-base font-semibold">Notifications</CardTitle>
      </CardHeader>
      <CardContent>
        {notifications.length === 0 ? (
          <EmptyState
            title="No notifications"
            description="Alerts for overdue or upcoming goals will appear here."
          />
        ) : (
          <div className="space-y-3">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                className="rounded-lg border bg-muted/20 p-3 transition-colors duration-150 hover:bg-muted/40"
              >
                <div className="mb-1 flex items-center justify-between gap-2">
                  <p className="text-sm font-medium">{notification.title}</p>
                  <Badge variant={severityVariant(notification.severity)}>
                    {notification.severity}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">{notification.message}</p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
