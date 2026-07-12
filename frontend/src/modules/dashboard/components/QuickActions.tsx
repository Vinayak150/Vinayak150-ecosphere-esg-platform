import { useNavigate } from "react-router-dom";

import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { EmptyState } from "@/shared/components/feedback/states";

import type { QuickAction } from "../types/dashboard.types";

interface QuickActionsProps {
  actions: QuickAction[];
}

export function QuickActions({ actions }: QuickActionsProps) {
  const navigate = useNavigate();
  const enabledActions = actions.filter((action) => action.enabled);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        {enabledActions.length === 0 ? (
          <EmptyState
            title="No actions available"
            description="Your role does not have quick actions enabled."
          />
        ) : (
          <div className="grid gap-2 sm:grid-cols-2">
            {enabledActions.map((action) => (
              <Button
                key={action.id}
                variant="outline"
                className="h-auto flex-col items-start gap-1 p-4 text-left"
                onClick={() => navigate(action.route)}
              >
                <span className="font-medium">{action.label}</span>
                <span className="text-xs font-normal text-muted-foreground">
                  {action.description}
                </span>
              </Button>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
