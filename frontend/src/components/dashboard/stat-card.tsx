"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

function StatCard({
  label,
  value,
  suffix,
  icon: Icon,
  trend,
  accent = "primary",
  delay = 0,
}: {
  label: string;
  value: string | number;
  suffix?: string;
  icon: LucideIcon;
  trend?: string;
  accent?: "primary" | "accent" | "warning";
  delay?: number;
}) {
  const accentClasses = {
    primary: "bg-primary-soft text-primary",
    accent: "bg-accent-soft text-accent",
    warning: "bg-warning-soft text-warning",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className="rounded-2xl border border-border bg-surface p-5"
    >
      <div className="flex items-center justify-between">
        <div className={cn("flex h-10 w-10 items-center justify-center rounded-xl", accentClasses[accent])}>
          <Icon className="h-5 w-5" />
        </div>
        {trend && <span className="text-xs font-medium text-accent">{trend}</span>}
      </div>
      <p className="mt-4 font-display text-2xl font-bold tracking-tight">
        {value}
        {suffix && <span className="text-base font-medium text-muted-foreground">{suffix}</span>}
      </p>
      <p className="mt-1 text-sm text-muted-foreground">{label}</p>
    </motion.div>
  );
}

export { StatCard };
