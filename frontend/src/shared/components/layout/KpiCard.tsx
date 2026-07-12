import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";

interface KpiCardProps {
  title: string;
  value: React.ReactNode;
  description?: string;
  icon: LucideIcon;
  index?: number;
  className?: string;
}

export function KpiCard({ title, value, description, icon: Icon, index = 0, className }: KpiCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.25 }}
      whileHover={{ y: -2 }}
    >
      <Card className={cn("overflow-hidden transition-shadow hover:shadow-md", className)}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10">
            <Icon className="h-4 w-4 text-primary" aria-hidden />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold tracking-tight">{value}</div>
          {description ? <p className="mt-1.5 text-xs text-muted-foreground">{description}</p> : null}
        </CardContent>
      </Card>
    </motion.div>
  );
}
