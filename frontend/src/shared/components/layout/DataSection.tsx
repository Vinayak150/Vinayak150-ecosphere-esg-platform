import type { ReactNode } from "react";

import { cn } from "@/shared/lib/utils";

interface DataSectionProps {
  title: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  contentClassName?: string;
  noPadding?: boolean;
}

export function DataSection({
  title,
  description,
  action,
  children,
  className,
  contentClassName,
  noPadding = false,
}: DataSectionProps) {
  return (
    <section
      className={cn(
        "overflow-hidden rounded-xl border bg-card text-card-foreground shadow-sm transition-shadow hover:shadow-md",
        className,
      )}
    >
      <div className="flex flex-col gap-3 border-b bg-muted/20 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div>
          <h2 className="text-base font-semibold tracking-tight">{title}</h2>
          {description ? <p className="mt-0.5 text-sm text-muted-foreground">{description}</p> : null}
        </div>
        {action ? <div className="shrink-0">{action}</div> : null}
      </div>
      <div className={cn(noPadding ? undefined : "p-0", contentClassName)}>{children}</div>
    </section>
  );
}
