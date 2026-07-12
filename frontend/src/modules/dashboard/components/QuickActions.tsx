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
        <CardTitle className="text-base font-semibold">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        {enabledActions.length === 0 ? (
          <EmptyState
            title="No actions available"
            description="Your role does not have quick actions enabled."
          />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {enabledActions.map((action) => (
              <Button
                key={action.id}
                variant="outline"
                className="h-auto flex-col items-start gap-1.5 rounded-xl p-4 text-left transition-all hover:border-primary/40 hover:bg-primary/5"
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
