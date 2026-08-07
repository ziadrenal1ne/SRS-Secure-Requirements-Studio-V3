import { cn } from "@/lib/utils";
import type { ProjectStatus } from "@/lib/types";
import { Circle } from "lucide-react";

const statusConfig: Record<ProjectStatus, { label: string; className: string; dot: string }> = {
  brouillon: { label: "Brouillon", className: "bg-surface-2 text-muted-foreground border-border", dot: "text-muted-foreground" },
  en_cours: { label: "En cours", className: "bg-primary-soft text-primary border-transparent", dot: "text-primary" },
  en_revue: { label: "En revue", className: "bg-warning-soft text-warning border-transparent", dot: "text-warning" },
  valide: { label: "Validé", className: "bg-accent-soft text-accent border-transparent", dot: "text-accent" },
};

function StatusChip({ status, className }: { status: ProjectStatus; className?: string }) {
  const config = statusConfig[status];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium",
        config.className,
        className
      )}
    >
      <Circle className={cn("h-1.5 w-1.5 fill-current", config.dot)} />
      {config.label}
    </span>
  );
}

export { StatusChip, statusConfig };
